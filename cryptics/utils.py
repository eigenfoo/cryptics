import dateutil
import re
from typing import List

import bs4
import numpy as np
import requests


def get_new_urls_from_sitemap(sitemap_url: str, known_urls: List[str], headers):
    response = requests.get(sitemap_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    urls = {url.text for url in soup.find_all("loc")}
    new_urls = list(urls - known_urls)
    return new_urls


def get_new_urls_from_nested_sitemaps(
    sitemap_url: str, nested_sitemap_regex: str, known_urls: List[str], headers
):
    response = requests.get(sitemap_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    nested_sitemaps = list(
        reversed(
            [
                sitemap.text
                for sitemap in soup.find_all("loc")
                if re.search(nested_sitemap_regex, sitemap.text)
            ]
        )
    )

    new_urls = []
    for nested_sitemap_url in nested_sitemaps:
        new_urls_ = get_new_urls_from_sitemap(nested_sitemap_url, known_urls, headers)
        new_urls.extend(new_urls_)

    return new_urls


def filter_saturday_urls(urls: List[str]):
    """
    Hex (a.k.a. Emily Cox & Henry Rathvon) only publish a cryptic in the
    National Post on Saturdays. On all other days, the blog reviews other
    cryptics (usually The Daily Telegraph, for which we have bigdave44).
    """
    return [
        url
        for url in urls
        if any([s in url.lower() for s in ["saturday", "cox", "rathvon"]])
    ]


def get_smallest_divs(soup):
    """Return the smallest (i.e. innermost, un-nested) `div` HTML tags."""
    return [
        div for div in soup.find_all("div") if not div.find("div") and div.text.strip()
    ]


def get_across_down_indexes(divs):
    (across_index,) = np.where([div.text.strip().lower() == "across" for div in divs])[
        0
    ]
    (down_index,) = np.where([div.text.strip().lower() == "down" for div in divs])[0]
    return across_index, down_index


def extract_puzzle_name(source_url: str, soup):
    d = {
        "bigdave44": lambda source_url, soup: (
            re.search("^[A-Za-z ]*[-—––:\s]*[0-9,]+", soup.find("title").text)
            .group()
            .replace("DT", "Daily Telegraph")
            .replace("ST", "Sunday Telegraph")
        ),
        "fifteensquared": lambda source_url, soup: (
            [s for s in source_url.split("/") if s][-1]
            .title()
            .replace("-", " ")
            .replace("By", "by")
        ),
        "natpostcryptic": lambda source_url, soup: (
            soup.find("title").text.replace(
                "National Post Cryptic Crossword Forum: ", ""
            )
        ),
        "thehinducrosswordcorner": lambda source_url, soup: (
            soup.find("title").text.replace("THE HINDU CROSSWORD CORNER: ", "")
        ),
        "times-xwd-times": lambda source_url, soup: (
            re.search(r"^[A-Za-z ]*[0-9,]+", soup.find("title").text).group()
        ),
    }
    for source_url_fragment, extract_puzzle_name_func in d.items():
        if source_url_fragment in source_url:
            return extract_puzzle_name_func(source_url, soup).strip()


def extract_puzzle_date(source_url: str, soup):
    d = {
        "bigdave44": lambda source_url, soup: (
            re.search(r"\d{4}/\d{2}/\d{2}", source_url).group().replace("/", "-")
        ),
        "fifteensquared": lambda source_url, soup: (
            re.search(r"\d{4}/\d{2}/\d{2}", source_url).group().replace("/", "-")
        ),
        "natpostcryptic": lambda source_url, soup: (
            dateutil.parser.parse(
                soup.find_all("h2", "date-header")[0].text.strip()
            ).strftime("%Y-%m-%d")
        ),
        "thehinducrosswordcorner": lambda source_url, soup: (
            dateutil.parser.parse(
                soup.find_all("h2", "date-header")[0].text.strip()
            ).strftime("%Y-%m-%d")
        ),
        "times-xwd-times": lambda source_url, soup: (
            dateutil.parser.parse(
                soup.find_all("div", attrs={"class": "asset-meta asset-entry-date"})[
                    0
                ].text.strip()
            ).strftime("%Y-%m-%d")
        ),
    }
    for source_url_fragment, extract_puzzle_date_func in d.items():
        if source_url_fragment in source_url:
            return extract_puzzle_date_func(source_url, soup).strip()


def extract_puzzle_url(soup):
    puzzle_url_regexes = [
        r"^https?://www.theguardian.com/crosswords/.+",
        r"^https?://puzzles.independent.co.uk/games/cryptic-crossword-independent/.+",
        r"^https?://www.ft.com/content/.+",
        r"^https?://www.thetimes.co.uk/puzzles/.+",
        r"^https?://puzzles.telegraph.co.uk/.+",
    ]
    try:
        puzzle_urls = [
            link.get("href")
            for link in soup.find_all(
                "a",
                attrs={
                    "href": lambda s: any(
                        [
                            bool(re.findall(puzzle_url_regex, s))
                            for puzzle_url_regex in puzzle_url_regexes
                        ]
                    )
                },
            )
        ]
    except:
        return None

    if len(puzzle_urls) == 1:
        return puzzle_urls[0].strip()

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
