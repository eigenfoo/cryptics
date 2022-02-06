import json
import logging
import re
import sqlite3
import time
from typing import List

import requests
import bs4

from cryptics.config import SITEMAPS, SQLITE_DATABASE


logging.basicConfig(level=logging.INFO)
headers = {
    "User-Agent": "cryptics.georgeho.org bot (https://cryptics.georgeho.org/)",
    "Accept-Encoding": "gzip",
}


def get_new_urls_from_sitemap(sitemap_url: str, known_urls: List[str]):
    response = requests.get(sitemap_url, headers=headers)
    soup = bs4.BeautifulSoup(response.text, "lxml")
    urls = {url.text for url in soup.find_all("loc")}
    new_urls = list(urls - known_urls)
    return new_urls


def get_new_urls_from_nested_sitemaps(
    sitemap_url: str, nested_sitemap_regex: str, known_urls: List[str]
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
        new_urls_ = get_new_urls_from_sitemap(nested_sitemap_url, known_urls)
        new_urls.extend(new_urls_)

    return new_urls


def get_new_urls(source, sitemap_url):
    with sqlite3.connect(SQLITE_DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT url FROM html WHERE source = '{source}';")
        known_urls = cursor.fetchall()
        known_urls = {url[0] for url in known_urls}

    if "bigdave44" in source:
        new_urls = get_new_urls_from_nested_sitemaps(
            sitemap_url,
            r"http://bigdave44.com/sitemap-[0-9]*.xml",
            known_urls,
        )
    elif "fifteensquared" in source:
        new_urls = get_new_urls_from_nested_sitemaps(
            sitemap_url,
            r"https://www.fifteensquared.net/wp-sitemap-posts-post-[0-9]*.xml",
            known_urls,
        )
    elif "natpostcryptic" in source:
        urls = get_new_urls_from_nested_sitemaps(
            sitemap_url,
            r"https://natpostcryptic.blogspot.com/sitemap.xml\?page=[0-9]*",
            known_urls,
        )
        # Hex (a.k.a. Emily Cox & Henry Rathvon) only publish a cryptic in the
        # National Post on Saturdays. On all other days, the blog reviews other
        # cryptics (usually The Daily Telegraph, for which we have bgidave44).
        new_urls = [
            url
            for url in urls
            if any([s in url.lower() for s in ["saturday", "cox", "ravthon"]])
        ]
    elif "thehinducrosswordcorner" in source:
        new_urls = get_new_urls_from_nested_sitemaps(
            sitemap_url,
            r"https://thehinducrosswordcorner.blogspot.com/sitemap.xml\?page=[0-9]*",
            known_urls,
        )
    elif "times_xwd_times" in source:
        new_urls = get_new_urls_from_sitemap(sitemap_url, known_urls)
    else:
        raise ValueError(f"Unrecognized source: {source}")

    return new_urls


def populate_db(sources, sleep_interval=20):
    for source, sitemap_url in sources.items():
        logging.info(f"Populating from {source}...")
        new_urls = get_new_urls(source, sitemap_url)
        logging.info(f"Found {len(new_urls)} new urls.")

        # Index `new_urls`
        for i, url in enumerate(new_urls):
            logging.info(f"{i} / {len(new_urls)}:\t{url}")
            response = requests.get(url, headers=headers)
            try:
                if not response.ok:
                    logging.error(f"Response not OK for {url}")
                    continue

                with sqlite3.connect(SQLITE_DATABASE) as conn:
                    cursor = conn.cursor()
                    sql = f"INSERT INTO html (source, url, html) VALUES (?, ?, ?)"
                    cursor.execute(sql, (source, url, response.text))
                    conn.commit()
            except:
                logging.error(f"Error inserting {url}")

            time.sleep(sleep_interval)


if __name__ == "__main__":
    populate_db(sources=SITEMAPS)
