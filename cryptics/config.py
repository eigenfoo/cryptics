import os
import json

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
