import dateutil
import re
from typing import List

import bs4
import numpy as np
import requests


PUZZLE_URL_REGEXES = [
    "^https?://www.theguardian.com/crosswords/.+",
    "^https?://puzzles.independent.co.uk/games/cryptic-crossword-independent/.+",
    "^https?://www.ft.com/content/.+",
    "^https?://www.thetimes.co.uk/puzzles/.+",
    "^https?://puzzles.telegraph.co.uk/.+",
]


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


def filter_saturday_urls(urls):
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


def extract_puzzle_name(source_url, soup):
    puzzle_name = None
    if "fifteensquared" in source_url:
        puzzle_name = (
            [s for s in source_url.split("/") if s][-1]
            .title()
            .replace("-", " ")
            .replace("By", "by")
        )
    elif "times-xwd-times" in source_url:
        title = soup.find("title").text
        puzzle_name = re.search("^[A-Za-z ]*[0-9,]+", title).group()
    elif "bigdave44" in source_url:
        title = soup.find("title").text
        puzzle_name = re.search("^[A-Za-z ]*[-—––:\s]*[0-9,]+", title).group()
        if "DT" in puzzle_name:
            puzzle_name = puzzle_name.replace("DT", "Daily Telegraph")
        elif "ST" in puzzle_name:
            puzzle_name = puzzle_name.replace("ST", "Sunday Telegraph")
    elif "thehinducrosswordcorner" in source_url:
        title = soup.find("title").text
        puzzle_name = title.replace("THE HINDU CROSSWORD CORNER: ", "")
    elif "natpostcryptic" in source_url:
        title = soup.find("title").text
        puzzle_name = title.replace("National Post Cryptic Crossword Forum: ", "")
    else:
        raise ValueError(f"Unknown source: {source_url}")

    return puzzle_name.strip()


def extract_puzzle_date(source_url, soup):
    puzzle_date = None
    if "fifteensquared" in source_url or "bigdave44" in source_url:
        puzzle_date = (
            re.search(r"\d{4}/\d{2}/\d{2}", source_url).group().replace("/", "-")
        )
    elif "times-xwd-times" in source_url:
        entry_date_div = soup.find_all(
            "div", attrs={"class": "asset-meta asset-entry-date"}
        )[0].text.strip()
        puzzle_date = dateutil.parser.parse(entry_date_div).strftime("%Y-%m-%d")
    elif "thehinducrosswordcorner" in source_url or "natpostcryptic" in source_url:
        date_header_h2 = soup.find_all("h2", "date-header")[0].text.strip()
        puzzle_date = dateutil.parser.parse(date_header_h2).strftime("%Y-%m-%d")
    else:
        raise ValueError(f"Unknown source: {source_url}")

    return puzzle_date.strip()


def extract_puzzle_url(soup):
    try:
        puzzle_urls = [
            link.get("href")
            for link in soup.find_all(
                "a",
                attrs={
                    "href": lambda s: any(
                        [
                            bool(re.findall(puzzle_url_regex, s))
                            for puzzle_url_regex in PUZZLE_URL_REGEXES
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
                            definitions.append("nan")
                        definitions.append(definition)
                        i += 1
                    else:
                        definitions.extend(j * ["nan"])
                        raw_definitions = [definition] + raw_definitions
                        i += j
                    is_first_definition = False
                    break

    if len(definitions) < len(clues):
        while len(definitions) < len(clues):
            definitions.append("nan")
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
            or definition == "nan"
            for (definition, clue) in zip(definitions, clues)
        ]
    ):
        return definitions
    else:
        raise RuntimeError("Produced mismatched definitions and clues")
