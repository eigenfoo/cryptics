import datetime
import json
import os

from utils import (
    get_new_urls_from_sitemap,
    get_new_urls_from_nested_sitemaps,
    filter_urls,
)


PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INITIALIZE_DB_SQL = os.path.join(PROJECT_DIR, "queries", "initialize-db.sql")
SQLITE_DATABASE = os.path.join(PROJECT_DIR, "cryptics.sqlite3")

# HTTP headers to use when scraping websites.
HEADERS = {
    "User-Agent": "cryptics.georgeho.org bot (https://cryptics.georgeho.org/)",
    "Accept-Encoding": "gzip",
}

# Names of blog sources and functions returning new URLs to scrape (given known URLs).
BLOG_SOURCES = {
    "bigdave44": lambda known_urls: get_new_urls_from_nested_sitemaps(
        "http://bigdave44.com/sitemap-index-1.xml",
        r"http://bigdave44.com/sitemap-[0-9]*.xml",
        known_urls,
        HEADERS,
    ),
    "fifteensquared": lambda known_urls: get_new_urls_from_nested_sitemaps(
        "https://www.fifteensquared.net/wp-sitemap.xml",
        r"https://www.fifteensquared.net/wp-sitemap-posts-post-[0-9]*.xml",
        known_urls,
        HEADERS,
    ),
    "natpostcryptic": lambda known_urls: filter_urls(
        get_new_urls_from_nested_sitemaps(
            "https://natpostcryptic.blogspot.com/sitemap.xml",
            r"https://natpostcryptic.blogspot.com/sitemap.xml\?page=[0-9]*",
            known_urls,
            HEADERS,
        ),
        ["saturday", "cox", "rathvon"],
    ),
    "thehinducrosswordcorner": lambda known_urls: get_new_urls_from_nested_sitemaps(
        "https://thehinducrosswordcorner.blogspot.com/sitemap.xml",
        r"https://thehinducrosswordcorner.blogspot.com/sitemap.xml\?page=[0-9]*",
        known_urls,
        HEADERS,
    ),
    "times_xwd_times": lambda known_urls: get_new_urls_from_sitemap(
        "https://times-xwd-times.livejournal.com/sitemap.xml",
        known_urls,
        HEADERS,
    ),
    "1across": lambda known_urls: filter_urls(
        get_new_urls_from_nested_sitemaps(
            "https://www.1across.org/sitemap.xml",
            r"https://www.1across.org/sitemap-[0-9]*.xml",
            known_urls,
            HEADERS,
        ),
        ["solutions", "annotations"],
    ),
}


def generate_newyorker_urls():
    # The date The New Yorker published their first cryptic crossword.
    start_date = datetime.date(2021, 6, 27)
    sunday = start_date
    today = datetime.date.today()
    while sunday <= today:
        yield f"https://www.newyorker.com/puzzles-and-games-dept/cryptic-crossword/{sunday.strftime('%Y/%m/%d')}"
        sunday = sunday + datetime.timedelta(days=7)


def generate_leoedit_urls():
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


AMUSELABS_SOURCES = {
    # Leo Edit has discontinued their cryptic, which I've already indexed. No
    # point doing it again.
    # "leoedit": generate_leoedit_urls,
    "newyorker": generate_newyorker_urls,
}
