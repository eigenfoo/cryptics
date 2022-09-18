from __future__ import annotations

import logging
import re
import sys
from typing import Callable, Iterable, List

import bs4
import numpy as np
import requests
from bs4 import BeautifulSoup
from dateutil import parser


def get_logger():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("cryptics.log"),
            logging.StreamHandler(sys.stderr),
        ],
    )
    return logging.getLogger(__name__)


def search(pattern: str, string: str, group: int = 0, **kwargs) -> str:
    """Scan through string looking for a match to the pattern.

    pattern: pattern to search for.
    string: string to search through.
    group: integer representing the capturing group to return (0 represents the
        entire match).
    """
    match = re.search(pattern, string, **kwargs)
    if match:
        return match.group(group)
    else:
        raise RuntimeError(f"No match for {pattern}")


def filter_strings_by_keyword(strings: Iterable[str], keywords: Iterable[str]):
    """Filter a list of strings to only those containing at least one keyword.

    strings: strings to filter
    keywords: keywords to filter strings by. Case insensitive.
    """
    return [
        string
        for string in strings
        if any([keyword.lower() in string.lower() for keyword in keywords])
    ]


PUZZLE_NAME_EXTRACTORS = {
    "bigdave44": lambda _, soup: (
        search(r"^[A-Za-z ]*[-—––:\s]*[0-9,]+", soup.find("title").text)
        .replace("DT", "Daily Telegraph")
        .replace("ST", "Sunday Telegraph")
    ),
    "fifteensquared": lambda source_url, _: (
        [s for s in source_url.split("/") if s][-1]
        .title()
        .replace("-", " ")
        .replace("By", "by")
    ),
    "natpostcryptic": lambda _, soup: (
        soup.find("title").text.replace("National Post Cryptic Crossword Forum: ", "")
    ),
    "thehinducrosswordcorner": lambda _, soup: (
        soup.find("title").text.replace("THE HINDU CROSSWORD CORNER: ", "")
    ),
    "times-xwd-times": lambda _, soup: (
        search(r"^[A-Za-z ]*[0-9,]+", soup.find("title").text)
    ),
}

PUZZLE_DATE_EXTRACTORS = {
    "bigdave44": lambda source_url, _: (
        search(r"\d{4}/\d{2}/\d{2}", source_url).replace("/", "-")
    ),
    "fifteensquared": lambda source_url, _: (
        search(r"\d{4}/\d{2}/\d{2}", source_url).replace("/", "-")
    ),
    "natpostcryptic": lambda _, soup: (
        parser.parse(soup.find("h2", "date-header").text.strip()).strftime("%Y-%m-%d")
    ),
    "thehinducrosswordcorner": lambda _, soup: (
        parser.parse(soup.find("h2", "date-header").text.strip()).strftime("%Y-%m-%d")
    ),
    "times-xwd-times": lambda _, soup: (
        parser.parse(
            soup.find("div", "asset-meta asset-entry-date").text.strip()
        ).strftime("%Y-%m-%d")
    ),
}


def _soup_to_puzzle_url(puzzle_url_regex: str) -> Callable[[None, BeautifulSoup], str]:
    # FIXME: why do I need to pull this out into a separate function? Is it
    # because of the nested lambdas?
    return lambda _, soup: soup.find(
        "a", attrs={"href": lambda s: bool(re.findall(puzzle_url_regex, s))}
    ).get("href")


PUZZLE_URL_EXTRACTORS = {
    source_url_fragment: _soup_to_puzzle_url(puzzle_url_regex)
    for source_url_fragment, puzzle_url_regex in [
        (
            "bigdave44",
            r"|".join(
                [
                    r"^https?://puzzles.telegraph.co.uk/.+",
                    r"^https?://www.telegraph.co.uk/puzzles/.+",
                ]
            ),
        ),
        (
            "fifteensquared",
            r"|".join(
                [
                    r"^https?://www.theguardian.com/crosswords/.+",
                    r"^https?://puzzles.independent.co.uk/games/cryptic-crossword-independent/.+",
                    r"^https?://www.ft.com/content/.+",
                ]
            ),
        ),
        ("times-xwd-times", r"^https?://www.thetimes.co.uk/puzzles/.+"),
    ]
}


def extract_string_from_url_and_soup(
    url: str,
    soup: BeautifulSoup,
    extractors: dict[str, Callable[[str, BeautifulSoup], str]],
) -> str | None:
    """TODO: document me!"""
    for source_url_fragment, extract_puzzle_name_func in extractors.items():
        if source_url_fragment in url:
            try:
                return extract_puzzle_name_func(url, soup).strip()
            except AttributeError:
                pass
    return None


def extract_definitions(soup, clues, raw_definitions):
    definitions = []
    i = 0

    is_first_definition = True
    while raw_definitions:
        definition = raw_definitions.pop(0)

        # If definition is in clue, add to `definitions` at appropriate place.
        if definition.strip() in clues[i]:
            if len(definitions) > 0:
                definitions[-1] = "/".join([definitions[-1], definition])
            else:
                definitions.append(definition)
            is_first_definition = False

        else:
            # Search for the next clue that contains this definition. Upon
            # finding one, handle it appropriately and stop looking.
            for j, clue in enumerate(clues[i + 1 :]):
                if definition in clue:
                    if j == 0:
                        if is_first_definition:
                            # Edge case: if the first clue lacks a definition,
                            # but the second clue has a definition.
                            definitions.append(None)
                        definitions.append(definition)
                        i += 1
                    else:
                        definitions.extend(j * [None])
                        raw_definitions = [definition] + raw_definitions
                        i += j
                    is_first_definition = False
                    break

    if len(definitions) < len(clues):
        while len(definitions) < len(clues):
            definitions.append(None)
    elif len(definitions) > len(clues):
        raise RuntimeError("More definitions than clues")

    if all(
        [
            all(
                [
                    s.strip().lower() in clue.lower()
                    for s in definition.strip().split("/")
                ]
            )
            or definition is None
            for (definition, clue) in zip(definitions, clues)
        ]
    ):
        return definitions
    else:
        raise RuntimeError("Produced mismatched definitions and clues")
