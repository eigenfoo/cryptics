from __future__ import annotations

import datetime
import json
import re
from os.path import abspath, dirname, join
from typing import Callable, Generator

import bs4
import requests

from cryptics.utils import filter_strings_by_keyword

PROJECT_DIR = dirname(dirname(abspath(__file__)))

TESTS_DIR = join(PROJECT_DIR, "tests")
TESTS_DATA_DIR = join(PROJECT_DIR, "tests/data")
INITIALIZE_DB_SQL = join(PROJECT_DIR, "queries", "initialize-db.sql")
SQLITE_DATABASE = join(PROJECT_DIR, "cryptics.sqlite3")

# HTTP headers to use when scraping websites.
HEADERS = {
    "User-Agent": "cryptics.georgeho.org bot (https://cryptics.georgeho.org/)",
    "Accept-Encoding": "gzip",
}

# Names of blog sources and functions returning new URLs to scrape (given known URLs).
BLOG_SOURCES: dict[str, Callable[[set[str]], set[str]]] = {
    "bigdave44": lambda known_urls: get_new_urls_from_nested_sitemaps(
        "http://bigdave44.com/sitemap-index-1.xml",
        r"http://bigdave44.com/sitemap-[0-9]*.xml",
        known_urls,
    ),
    "fifteensquared": lambda known_urls: get_new_urls_from_nested_sitemaps(
        "https://www.fifteensquared.net/wp-sitemap.xml",
        r"https://www.fifteensquared.net/wp-sitemap-posts-post-[0-9]*.xml",
        known_urls,
    ),
    # Hex (a.k.a. Emily Cox & Henry Rathvon) only publish a cryptic in the
    # National Post on Saturdays. On all other days, the blog reviews other
    # cryptics (usually The Daily Telegraph, for which we have bigdave44).
    "natpostcryptic": lambda known_urls: filter_strings_by_keyword(
        get_new_urls_from_nested_sitemaps(
            "https://natpostcryptic.blogspot.com/sitemap.xml",
            r"https://natpostcryptic.blogspot.com/sitemap.xml\?page=[0-9]*",
            known_urls,
        ),
        ["saturday", "cox", "rathvon"],
    ),
    "thehinducrosswordcorner": lambda known_urls: get_new_urls_from_nested_sitemaps(
        "https://thehinducrosswordcorner.blogspot.com/sitemap.xml",
        r"https://thehinducrosswordcorner.blogspot.com/sitemap.xml\?page=[0-9]*",
        known_urls,
    ),
    # As of May 15, 2022, Times for the Times has migrated from
    # times-xwd-times.livejournal.com to timesforthetimes.co.uk See
    # https://times-xwd-times.livejournal.com/2740044.html for more.
    # "times_xwd_times": lambda known_urls: get_new_urls_from_sitemap(
    #     "https://times-xwd-times.livejournal.com/sitemap.xml",
    #     known_urls,
    # ),
    "1across": lambda known_urls: filter_strings_by_keyword(
        get_new_urls_from_nested_sitemaps(
            "https://www.1across.org/sitemap.xml",
            r"https://www.1across.org/sitemap-[0-9]*.xml",
            known_urls,
        ),
        ["solutions", "annotations"],
    ),
    # thenationcryptic only publishes solutions on blog posts titled "Solution"
    # (mainly for The Nation puzzles).
    "thenationcryptic": lambda known_urls: filter_strings_by_keyword(
        get_new_urls_from_nested_sitemaps(
            "https://thenationcryptic.blogspot.com/sitemap.xml",
            r"https://thenationcryptic.blogspot.com/sitemap.xml\?page=[0-9]*",
            known_urls,
        ),
        ["solution", "solutions"],
    ),
}


def get_new_urls_from_sitemap(
    sitemap_url: str, known_urls: set[str], headers: dict[str, str] = HEADERS
) -> set[str]:
    response = requests.get(sitemap_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    urls = {url.text for url in soup.find_all("loc")}
    new_urls = set(urls - known_urls)
    return new_urls


def get_new_urls_from_nested_sitemaps(
    sitemap_url: str,
    nested_sitemap_regex: str,
    known_urls: set[str],
    headers: dict[str, str] = HEADERS,
) -> set[str]:
    response = requests.get(sitemap_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    nested_sitemaps = set(
        reversed(
            [
                sitemap.text
                for sitemap in soup.find_all("loc")
                if re.search(nested_sitemap_regex, sitemap.text)
            ]
        )
    )

    new_urls = set()
    for nested_sitemap_url in nested_sitemaps:
        new_urls_ = get_new_urls_from_sitemap(nested_sitemap_url, known_urls, headers)
        new_urls.update(new_urls_)

    return new_urls


def generate_newyorker_urls() -> Generator[str, None, None]:
    # The date The New Yorker published their first cryptic crossword.
    start_date = datetime.date(2021, 6, 27)
    sunday = start_date
    today = datetime.date.today()
    while sunday <= today:
        yield f"https://www.newyorker.com/puzzles-and-games-dept/cryptic-crossword/{sunday.strftime('%Y/%m/%d')}"
        sunday = sunday + datetime.timedelta(days=7)


def generate_leoedit_urls() -> Generator[str, None, None]:
    # LEO Edit seems to reject programmatic HTML requests, and I can't figure
    # out how to circumvent. Instead, I've found the Amuselabs CDN URLs by
    # hand.
    yield from [
        f"https://cdn2.amuselabs.com/pmm/crossword?id={id_}&set=leoedit"
        for id_ in [
            "d9f78a7a",
            "074b8679",
            "51173ffb",
            "b6edbf48",
            "1bd35ce3",
            "64486a16",
            "7656be6a",
        ]
    ]


AMUSELABS_SOURCES: dict[str, Generator[str, None, None]] = {
    # Leo Edit has discontinued their cryptic, which I've already indexed. No
    # point doing it again.
    # "leoedit": generate_leoedit_urls(),
    "newyorker": generate_newyorker_urls(),
}
