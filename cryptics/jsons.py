import logging
import os
import sqlite3
import json
from datetime import datetime
from bs4 import BeautifulSoup
from glob import glob

import numpy as np
import pandas as pd

from cryptics.config import SQLITE_DATABASE


def parse_json(puzzle):
    clues = [placed_word["clue"]["clue"] for placed_word in puzzle["placedWords"]]
    clues = [BeautifulSoup(clue, "lxml").text for clue in clues]
    answers = [placed_word["word"] for placed_word in puzzle["placedWords"]]
    answers = [BeautifulSoup(answer, "lxml").text for answer in answers]
    try:
        annotations = [
            placed_word["clue"]["refText"] for placed_word in puzzle["placedWords"]
        ]
    except KeyError:
        annotations = ["nan" for _ in clues]
    definitions = ["nan" for _ in clues]
    clue_numbers = [
        str(placed_word["clueNum"]) + ("a" if placed_word["acrossNotDown"] else "d")
        for placed_word in puzzle["placedWords"]
    ]

    data = pd.DataFrame(
        data=[clue_numbers, answers, clues, annotations, definitions],
        index=["clue_number", "answer", "clue", "annotation", "definition"],
    ).T

    data["source"] = "newyorker"
    data["puzzle_url"] = url
    data["source_url"] = url
    data["puzzle_name"] = puzzle["title"]
    data["puzzle_date"] = datetime.utcfromtimestamp(
        puzzle["publishTime"] / 1000
    ).strftime("%Y-%m-%d")
    return data


if __name__ == "__main__":
    with sqlite3.connect(SQLITE_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT url FROM json WHERE NOT is_parsed;")
        urls_to_parse = cursor.fetchall()
        urls_to_parse = {url[0] for url in urls_to_parse}

    for url in urls_to_parse:
        print(f"Parsing {url}")
        with sqlite3.connect(SQLITE_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT json FROM json WHERE url = '{url}';")
            puzzle_json = cursor.fetchone()[0]

        puzzle = json.loads(puzzle_json)
        try:
            data = parse_json(puzzle)
            print(f"\tSuccess!")
        except:
            continue

        with sqlite3.connect(SQLITE_DATABASE) as conn:
            data.to_sql(f"clues", conn, if_exists="append", index=False)
            cursor = conn.cursor()
            sql = f"UPDATE json SET is_parsed = TRUE, datetime_parsed = datetime('now') WHERE url = '{url}';"
            cursor.execute(sql)
