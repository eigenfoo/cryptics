import argparse
import logging
import os
import sqlite3
from glob import glob

import numpy as np
import pandas as pd
import puz

from cryptics.config import SQLITE_DATABASE
from cryptics.utils import get_logger, last_dirname_basename


def insert_puz(source: str, path: str, puz_filename: str):
    with open(puz_filename, "rb") as f:
        puz_blob = f.read()

    with sqlite3.connect(SQLITE_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO raw (source, location, content_type, content) VALUES (?, ?, 'puz', ?)",
            (source, path, puz_blob),
        )
        conn.commit()


def parse_puz(puz_filename: str):
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
    definitions = len(clues) * [None]
    annotations = len(clues) * [None]
    clue_numbers = [str(clue["num"]) + "a" for clue in numbering.across] + [
        str(clue["num"]) + "d" for clue in numbering.down
    ]
    puzzle_dates = len(clues) * [None]
    puzzle_names = [puzzle.title for _ in range(len(clues))]
    puzzle_urls = len(clues) * [None]
    source_urls = [last_dirname_basename(puz_filename) for _ in range(len(clues))]

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
    logger = get_logger()

    parser = argparse.ArgumentParser()
    parser.add_argument("--puz-glob", type=str, required=True)
    parser.add_argument("--source", type=str, required=True)
    args = parser.parse_args()

    with sqlite3.connect(SQLITE_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT source_url FROM clues;")
        known_urls = {url for url, in cursor.fetchall()}

    new_puz_filenames = {
        puz_filename
        for puz_filename in glob(args.puz_glob)
        if last_dirname_basename(puz_filename) not in known_urls
    }

    for puz_filename in new_puz_filenames:
        logger.info(f"Parsing: {puz_filename}")
        data = parse_puz(puz_filename)
        data["source"] = args.source
        with sqlite3.connect(SQLITE_DATABASE) as conn:
            data.to_sql(f"clues", conn, if_exists="append", index=False)

        insert_puz(args.source, last_dirname_basename(puz_filename), puz_filename)
