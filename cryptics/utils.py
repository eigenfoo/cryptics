from __future__ import annotations

import logging
import re
import sys
from re import Match
from typing import Any, Callable, Iterable, List

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


def match(pattern: str, string: str, **kwargs) -> Match[str]:
    """Call re.match and raise an error if no match is found.

    pattern: pattern to search for.
    string: string to search through.
    """
    match = re.match(pattern, string, **kwargs)
    if match:
        return match
    else:
        raise RuntimeError(f"No match for {pattern}")


def search(pattern: str, string: str, **kwargs) -> Match[str]:
    """Call re.search and raise an error if no match is found.

    pattern: pattern to search for.
    string: string to search through.
    """
    match = re.search(pattern, string, **kwargs)
    if match:
        return match
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
        .group()
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
        search(r"^[A-Za-z ]*[0-9,]+", soup.find("title").text).group()
    ),
}

PUZZLE_DATE_EXTRACTORS = {
    "bigdave44": lambda source_url, _: (
        search(r"\d{4}/\d{2}/\d{2}", source_url).group().replace("/", "-")
    ),
    "fifteensquared": lambda source_url, _: (
        search(r"\d{4}/\d{2}/\d{2}", source_url).group().replace("/", "-")
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


def _soup_to_puzzle_url(puzzle_url_regex: str) -> Callable[[Any, BeautifulSoup], str]:
    # TODO: If I move this inside PUZZLE_URL_EXTRACTORS, the unit tests will fail.
    # Why do I need to pull this out into a separate function? Is it because of
    # the nested lambdas?
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


def align_suspected_definitions_with_clues(
    clues: list[str], suspected_definitions: list[str]
):
    """Given a list of clues and a list of strings that may or may not be
    definitions, produce a list of definitions.

    This function should be used when clues can be reliably extracted from a
    web page's HTML, but definitions within clues are not reliably indicated
    with HTML tags: simply pass the clues and best "suspected definitions", and
    this function will "align" them correctly. See the unit tests for examples.
    Note that this function is case sensitive.

    clues: list of clues.
    suspected_definitions: a list of suspected definitions. Definitions may be
        missing and (in the case of double definition clues) spread out over
        multiple suspected definitions.
    """
    # This code is a lot more readable if we use empty strings (instead of
    # Nones) when we lack a definition. We will convert them back to Nones later.
    definitions: list[str] = []
    clue_index: int = 0

    for suspected_definition in suspected_definitions:
        # If suspected_definition is in clue...
        if suspected_definition.strip() in clues[clue_index]:
            # add it to the latest definition...
            if definitions:
                definitions[-1] = "/".join([definitions[-1], suspected_definition])
            # ... unless we have no definitions yet, in which case let this be
            # our first definition.
            else:
                definitions = [suspected_definition]

        # Otherwise, if suspected_definition is not in clue...
        else:
            # search for the next clue that contains suspected_definition...
            for lookahead_index, clue in enumerate(clues[clue_index + 1 :]):
                # and upon finding it:
                # (a) add it to definitions, but only after adding empty
                #     strings for each clue we find that does not contain the
                #     suspected definition, as we must lack definitions for
                #     these clues.
                # (b) increment the clue_index. TODO: why max(1,
                #     lookahead_index + 1)?
                # (c) stop searching for clues containing suspected_definition.
                if suspected_definition.strip() in clue:
                    # In the edge case where we have no definitions yet, pad
                    # them with empty strings. TODO: why max(1, lookahead_index)?
                    if not definitions:
                        definitions = (clue_index + max(1, lookahead_index)) * [""]

                    definitions.extend(lookahead_index * [""] + [suspected_definition])
                    clue_index += max(1, lookahead_index + 1)
                    break

    # Top up definitions to be of equal length to clues.
    if len(definitions) < len(clues):
        definitions.extend((len(clues) - len(definitions)) * [""])
    # Fail if we've somehow produced more definitions than clues.
    elif len(definitions) > len(clues):
        raise RuntimeError(f"Produced more definitions than clues: {definitions}")

    if not all(
        [
            # Note all([]) evaluates to True, in the case of definition == "".
            all(
                [
                    s.strip().lower() in clue.lower()
                    for s in definition.strip().split("/")
                ]
            )
            for (definition, clue) in zip(definitions, clues)
        ]
    ):
        raise RuntimeError("Produced mismatched definitions and clues.")

    # Immediately before returning, replace empty strings with Nones.
    return [definition if definition else None for definition in definitions]
