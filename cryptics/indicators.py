import re
import sqlite3
from typing import Dict, List
import pandas as pd
from tqdm import tqdm


INDICATOR_REGEXES = {
    "anagram": [r"anagram \(([A-Z]?[a-z ]+)\)"],
    "container": [
        r"contain \(([A-Z]?[a-z ]+)\)",
        r"contains \(([A-Z]?[a-z ]+)\)",
        r"containing \(([A-Z]?[a-z ]+)\)",
    ],
    "deletion": [],
    "hidden": [r"hidden \(([A-Z]?[a-z ]+)\)"],
    "homophone": [r"homophone \(([A-Z]?[a-z ]+)\)", r"sounds like \(([A-Z]?[a-z ]+)\)"],
    "reversal": [r"reversal \(([A-Z]?[a-z ]+)\)"],
}


def find_and_write_indicators(
    annotation: str,
    indicator_regexes: Dict[str, List[str]],
    write_cursor: sqlite3.Cursor,
):
    for wordplay, regexes in indicator_regexes.items():
        for regex in regexes:
            # FIXME: is it a good idea to indiscriminately .lower() like this?
            # Perhaps I should only lower if I'm sure it's in titlecase?
            indicators = "/".join([s.strip().lower() for s in re.findall(regex, annotation)])
            if indicators:
                try:
                    write_cursor.execute(
                        f"INSERT INTO indicators (clue_rowid) VALUES ({row_id});"
                    )
                except sqlite3.IntegrityError:
                    pass
                write_cursor.execute(
                    f"UPDATE indicators SET {wordplay} = ? WHERE clue_rowid = ?;",
                    (indicators, row_id),
                )


def unpivot_indicators_table():
    with sqlite3.connect("cryptics.sqlite3") as conn:
        df = pd.read_sql("SELECT * FROM indicators;", conn)

    df = df.melt(id_vars=["clue_rowid"], var_name="wordplay", value_name="indicator")
    df = df[df["indicator"].str.strip() != ""]
    df = (
        df.groupby(["wordplay", "indicator"])["clue_rowid"]
        .agg(lambda group: ", ".join([f"[{s}](/data/clues/{s})" for s in group]))
        .to_frame()
        .rename(columns={"clue_rowid": "clue_rowids"})
        .reset_index()
    )

    with sqlite3.connect("cryptics.sqlite3") as conn:
        df.to_sql("indicators_unpivoted", conn, if_exists="replace", index=False)


if __name__ == "__main__":
    with sqlite3.connect("cryptics.sqlite3") as conn:
        read_cursor = conn.cursor()
        write_cursor = conn.cursor()
        read_cursor.execute("SELECT rowid, annotation FROM clues;")

        for (row_id, annotation) in tqdm(read_cursor, desc="Finding indicators"):
            if not annotation:
                continue
            find_and_write_indicators(annotation, INDICATOR_REGEXES, write_cursor)

        conn.commit()

    unpivot_indicators_table()
