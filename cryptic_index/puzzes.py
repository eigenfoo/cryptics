import argparse
import logging
import os
import pathlib
import sqlite3
from datetime import datetime
from glob import glob

import numpy as np
import pandas as pd
import puz


def parse_puz(puz_filename):
    puzzle = puz.read(puz_filename)
    numbering = puzzle.clue_numbering()

    clues = [clue["clue"] for clue in (numbering.across + numbering.down)]
    answers = [
        "".join(puzzle.solution[clue["cell"] + i] for i in range(clue["len"]))
        for clue in numbering.across
    ] + [
        "".join(
            puzzle.solution[clue["cell"] + i * numbering.width]
            for i in range(clue["len"])
        )
        for clue in numbering.down
    ]
    definitions = [None for _ in range(len(clues))]
    annotations = [None for _ in range(len(clues))]
    clue_numbers = [str(clue["num"]) + "a" for clue in numbering.across] + [
        str(clue["num"]) + "d" for clue in numbering.down
    ]
    puzzle_dates = [
        datetime.fromtimestamp(pathlib.Path(puz_filename).stat().st_ctime).strftime(
            "%Y-%m-%d"
        )
        for _ in range(len(clues))
    ]
    puzzle_names = [puzzle.title for _ in range(len(clues))]
    puzzle_urls = [None for _ in range(len(clues))]
    source_urls = [
        os.path.join(
            os.path.basename(os.path.dirname(puz_filename)),
            os.path.basename(puz_filename),
        )
        for _ in range(len(clues))
    ]

    return pd.DataFrame(
        data=np.array(
            [
                clues,
                answers,
                definitions,
                annotations,
                clue_numbers,
                puzzle_dates,
                puzzle_names,
                puzzle_urls,
                source_urls,
            ]
        ).T,
        columns=[
            "clue",
            "answer",
            "definition",
            "annotation",
            "clue_number",
            "puzzle_date",
            "puzzle_name",
            "puzzle_url",
            "source_url",
        ],
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--puz-glob", type=str, required=True)
    parser.add_argument("--source", type=str, required=True)
    args = parser.parse_args()

    puz_filenames = sorted(glob(args.puz_glob))
    for puz_filename in puz_filenames:
        logging.info(f"Parsing {puz_filename}")
        data = parse_puz(puz_filename)
        with sqlite3.connect("cryptics.sqlite3") as conn:
            data.to_sql(f"parsed_{args.source}", conn, if_exists="append", index=False)
