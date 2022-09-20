import json
import logging
import sqlite3
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup

from cryptics.config import SQLITE_DATABASE
from cryptics.utils import get_logger


def parse_json(puzzle: dict, source: str) -> pd.DataFrame:
    clues = [placed_word["clue"]["clue"] for placed_word in puzzle["placedWords"]]
    clues = [BeautifulSoup(clue, "lxml").text for clue in clues]
    try:
        answers = [placed_word["word"] for placed_word in puzzle["placedWords"]]
    except KeyError:
        answers = [placed_word["originalTerm"] for placed_word in puzzle["placedWords"]]
    answers = [BeautifulSoup(answer, "lxml").text for answer in answers]
    try:
        annotations = [
            placed_word["clue"]["refText"] for placed_word in puzzle["placedWords"]
        ]
    except KeyError:
        annotations = [None for _ in clues]
    definitions = [None for _ in clues]
    clue_numbers = [
        str(placed_word["clueNum"]) + ("a" if placed_word["acrossNotDown"] else "d")
        for placed_word in puzzle["placedWords"]
    ]

    data = pd.DataFrame(
        data=[clue_numbers, answers, clues, annotations, definitions],
        index=["clue_number", "answer", "clue", "annotation", "definition"],
    ).T

    data["source"] = source
    data["puzzle_url"] = url
    data["source_url"] = url
    data["puzzle_name"] = puzzle["title"]
    data["puzzle_date"] = datetime.utcfromtimestamp(
        puzzle["publishTime"] / 1000
    ).strftime("%Y-%m-%d")
    return data


if __name__ == "__main__":
    logger = get_logger()

    with sqlite3.connect(SQLITE_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT DISTINCT location FROM raw WHERE content_type = 'json' AND NOT is_parsed;"
        )
        urls_to_parse = {url for url, in cursor.fetchall()}

    for url in urls_to_parse:
        logger.info(f"Parsing: {url}")
        with sqlite3.connect(SQLITE_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT content, source FROM raw WHERE location = '{url}';")
            puzzle_json, source = cursor.fetchone()

        puzzle = json.loads(puzzle_json)

        try:
            data = parse_json(puzzle, source)
            logger.info(f"Successfully parsed: {url}")
        except:
            logger.error(f"Failed to parse: {url}", exc_info=True)
            continue

        with sqlite3.connect(SQLITE_DATABASE) as conn:
            data.to_sql(f"clues", conn, if_exists="append", index=False)
            cursor = conn.cursor()
            sql = f"UPDATE raw SET is_parsed = TRUE, datetime_parsed = datetime('now') WHERE location = '{url}';"
            cursor.execute(sql)
