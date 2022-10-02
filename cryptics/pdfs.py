import argparse
import logging
import os
import sqlite3
from collections import Counter
from glob import glob
from itertools import combinations
from typing import Iterable

import numpy as np
import pandas as pd
import puz

from cryptics.config import SQLITE_DATABASE
from cryptics.utils import get_logger, last_dirname_basename


def pair_strings(
    strings: Iterable[str], extra_words: list[str]
) -> set[tuple[str, str]]:
    """Pairs a list of strings with extra_words."""
    pairs: set[tuple[str, str]] = set()
    for first, second in combinations(strings, 2):
        # TODO: this requires _all_ of the extra words... it should be _any_
        if Counter(first.lower().split() + extra_words) == Counter(
            second.lower().split()
        ):
            pairs.add((first, second))
    return pairs


if __name__ == "__main__":
    # logger = get_logger()
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--glob", type=str, required=True)
    # parser.add_argument("--source", type=str, required=True)
    # args = parser.parse_args()

    with sqlite3.connect(SQLITE_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT DISTINCT source_url FROM clues;")
        known_urls = {url for url, in cursor.fetchall()}

    new_pdf_filenames = {
        pdf_filename
        for pdf_filename in glob("/home/george/puzzlecrypt/*.pdf")
        if last_dirname_basename(pdf_filename) not in known_urls
    }

    paired_puzzle_solution_pdfs = pair_strings(new_pdf_filenames, ["solution"])

    for puzzle_pdf, solution_pdf in paired_puzzle_solution_pdfs:
        pass
