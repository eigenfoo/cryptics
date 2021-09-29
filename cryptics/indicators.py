import re
import sqlite3
from typing import Dict, List
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
            indicators = "/".join(re.findall(regex, annotation))
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


if __name__ == "__main__":
    with sqlite3.connect("cryptics.sqlite3") as conn:
        read_cursor = conn.cursor()
        write_cursor = conn.cursor()
        read_cursor.execute("SELECT rowid, annotation FROM clues;")

        for (row_id, annotation) in tqdm(read_cursor):
            if not annotation:
                continue
            find_and_write_indicators(annotation, INDICATOR_REGEXES, write_cursor)

        conn.commit()
