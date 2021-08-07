import datetime
import json
import logging
import re
import sqlite3
import time

import requests
import bs4


SITEMAP_URLS = {
    "raw_fifteensquared": "https://www.fifteensquared.net/wp-sitemap.xml",
    "raw_times_xwd_times": "https://times-xwd-times.livejournal.com/sitemap.xml",
    "raw_bigdave44": "http://bigdave44.com/sitemap-index-1.xml",
}

logging.basicConfig(level=logging.INFO)
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "Accept-Encoding": "gzip",
}


def get_new_urls(site):
    with sqlite3.connect("cryptics.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT url FROM {site};")
        known_urls = cursor.fetchall()
        known_urls = {url[0] for url in known_urls}

    if "fifteensquared" in site:
        sitemap = SITEMAP_URLS[site]
        response = requests.get(sitemap, headers=headers)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        sitemaps = list(
            reversed(
                [
                    sitemap.text
                    for sitemap in soup.find_all("sitemap")
                    if re.search(
                        # Just 7/8/9/10 for now...
                        r"https://www.fifteensquared.net/wp-sitemap-posts-post-(7|8|9|10).xml",
                        sitemap.text,
                    )
                ]
            )
        )
        new_urls = []
        for sitemap in sitemaps:
            response = requests.get(sitemap, headers=headers)
            soup = bs4.BeautifulSoup(response.text, "lxml")
            urls = {url.text for url in soup.find_all("url")}
            new_urls.extend(list(urls - known_urls))

    elif "bigdave44" in site:
        sitemap = SITEMAP_URLS[site]
        response = requests.get(sitemap, headers=headers)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        sitemaps = list(
            reversed(
                [
                    sitemap.text
                    for sitemap in soup.find_all("loc")
                    if re.search(
                        # Just 4/5/6 for now...
                        r"http://bigdave44.com/sitemap-(4|5|6).xml",
                        sitemap.text,
                    )
                ]
            )
        )
        new_urls = []
        for sitemap in sitemaps:
            response = requests.get(sitemap, headers=headers)
            soup = bs4.BeautifulSoup(response.text, "lxml")
            urls = {url.text for url in soup.find_all("loc")}
            new_urls.extend(list(urls - known_urls))

    elif "times_xwd_times" in site:
        sitemap = SITEMAP_URLS[site]
        response = requests.get(sitemap, headers=headers)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        urls = {url.text for url in soup.find_all("loc")}
        new_urls = list(urls - known_urls)

    return new_urls


if __name__ == "__main__":
    for site, sitemap_url in SITEMAP_URLS.items():
        new_urls = get_new_urls(site)

        logging.info(f"Found {len(new_urls)} new urls.")

        # Index `new_urls`
        for i, url in enumerate(new_urls):
            logging.info(f"{i} / {len(new_urls)}:\t{url}")
            response = requests.get(url, headers=headers)
            try:
                if not response.ok:
                    logging.error(f"Response not OK for {url}")
                    continue

                with sqlite3.connect("cryptics.sqlite3") as conn:
                    cursor = conn.cursor()
                    sql = f"INSERT INTO {site} (url, html) VALUES (?, ?)"
                    cursor.execute(sql, (url, response.text))
                    conn.commit()
            except:
                logging.error(f"Error inserting {url}")

            time.sleep(20)
