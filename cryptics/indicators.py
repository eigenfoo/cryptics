import re
import sqlite3
from typing import Dict, List
import pandas as pd
from tqdm import tqdm

from cryptics.config import SQLITE_DATABASE, INITIALIZE_DB_SQL


INDICATOR_REGEXES = {
    "anagram": [
        r"anagram \(([A-Z]?[a-z ]+)\)",
        r"anagram of \(([A-Z]?[a-z ]+)\)",
        r"anagrammed \(([A-Z]?[a-z ]+)\)",
    ],
    "container": [
        r"contain \(([A-Z]?[a-z ]+)\)",
        r"contains \(([A-Z]?[a-z ]+)\)",
        r"containing \(([A-Z]?[a-z ]+)\)",
    ],
    "insertion": [
        r"contained in \(([A-Z]?[a-z ]+)\)",
        r"inserted into \(([A-Z]?[a-z ]+)\)",
        r"within \(([A-Z]?[a-z ]+)\)",
    ],
    "deletion": [
        r"deleted \(([A-Z]?[a-z ]+)\)",
        r"deletion \(([A-Z]?[a-z ]+)\)",
        r"removed \(([A-Z]?[a-z ]+)\)",
    ],
    "hidden": [
        r"hidden \(([A-Z]?[a-z ]+)\)",
        r"hidden in \(([A-Z]?[a-z ]+)\)",
    ],
    "homophone": [
        r"homophone \(([A-Z]?[a-z ]+)\)",
        r"sound like \(([A-Z]?[a-z ]+)\)",
        r"sounds like \(([A-Z]?[a-z ]+)\)",
    ],
    "reversal": [
        r"reversing \(([A-Z]?[a-z ]+)\)",
        r"reversal \(([A-Z]?[a-z ]+)\)",
        r"reverse \(([A-Z]?[a-z ]+)\)",
        r"reversed \(([A-Z]?[a-z ]+)\)",
    ],
}

CHARADE_REGEXES = [r"([A-Z][A-Z ]+)\s?\(([A-Z]?[a-z ]+)\)"]


def find_and_write_indicators(
    clue_row_id: int,
    clue: str,
    annotation: str,
    indicator_regexes: Dict[str, List[str]],
    write_cursor: sqlite3.Cursor,
):
    for wordplay, regexes in indicator_regexes.items():
        for regex in regexes:
            indicators = [
                s.strip().lower()
                for s in re.findall(regex, annotation)
                if s.strip().lower() in clue.lower()
            ]
            indicators = "/".join(indicators)
            if indicators:
                try:
                    write_cursor.execute(
                        f"INSERT INTO indicators (clue_rowid) VALUES ({clue_row_id});"
                    )
                except sqlite3.IntegrityError:
                    pass
                write_cursor.execute(
                    f"UPDATE indicators SET {wordplay} = ? WHERE clue_rowid = ?;",
                    (indicators, clue_row_id),
                )


def find_and_write_charades(
    clue_row_id: int,
    clue: str,
    annotation: str,
    charade_regexes: List[str],
    write_cursor: sqlite3.Cursor,
):
    for regex in charade_regexes:
        charades = [
            (clue_row_id, charade.strip(), answer.strip())
            for (answer, charade) in re.findall(regex, annotation)
            if charade.strip().lower() in clue.lower() and answer.isupper()
        ]
        if charades:
            sql = "INSERT INTO charades (clue_rowid, charade, answer) VALUES (?, ?, ?);"
            write_cursor.executemany(sql, charades)


def unpivot_indicators_table():
    with sqlite3.connect(SQLITE_DATABASE) as conn:
        df = pd.read_sql("SELECT * FROM indicators;", conn)
    df = df.melt(id_vars=["clue_rowid"], var_name="wordplay", value_name="indicator")
    df = df[df["indicator"].str.strip() != ""]
    df["indicator"] = df["indicator"].apply(lambda s: s.split("/"))
    df = df.explode("indicator")
    df = (
        df.groupby(["wordplay", "indicator"])["clue_rowid"]
        .agg(lambda group: ", ".join([f"[{s}](/data/clues/{s})" for s in group]))
        .to_frame()
        .rename(columns={"clue_rowid": "clue_rowids"})
        .reset_index()
    )
    with sqlite3.connect(SQLITE_DATABASE) as conn:
        df.to_sql("indicators_unpivoted", conn, if_exists="replace", index=False)


def unpivot_charades_table():
    with sqlite3.connect(SQLITE_DATABASE) as conn:
        df = pd.read_sql("SELECT * FROM charades;", conn)
    df = (
        df.groupby(["charade", "answer"])["clue_rowid"]
        .agg(lambda group: ", ".join([f"[{s}](/data/clues/{s})" for s in group]))
        .to_frame()
        .rename(columns={"clue_rowid": "clue_rowids"})
        .reset_index()
    )
    with sqlite3.connect(SQLITE_DATABASE) as conn:
        df.to_sql("charades_unpivoted", conn, if_exists="replace", index=False)


if __name__ == "__main__":
    with sqlite3.connect(SQLITE_DATABASE) as conn:
        read_cursor = conn.cursor()
        write_cursor = conn.cursor()

        write_cursor.execute("DROP TABLE IF EXISTS charades;")
        write_cursor.execute("DROP TABLE IF EXISTS indicators;")
        with open(INITIALIZE_DB_SQL, "r") as f:
            sql = f.read()
        write_cursor.executescript(sql)
        conn.commit()

        read_cursor.execute("SELECT rowid, clue, annotation FROM clues;")
        for (clue_row_id, clue, annotation) in tqdm(
            read_cursor, desc="Finding indicators"
        ):
            if not annotation:
                continue
            find_and_write_indicators(
                clue_row_id, clue, annotation, INDICATOR_REGEXES, write_cursor
            )
            find_and_write_charades(
                clue_row_id, clue, annotation, CHARADE_REGEXES, write_cursor
            )
        conn.commit()

    unpivot_indicators_table()
    unpivot_charades_table()
