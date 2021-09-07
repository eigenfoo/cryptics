import json
import logging
import re
import sqlite3
import time

import requests
import bs4


logging.basicConfig(level=logging.INFO)
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "Accept-Encoding": "gzip",
}


def get_new_urls(source, sitemap_url):
    with sqlite3.connect("cryptics.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT url FROM html WHERE source = '{source}';")
        known_urls = cursor.fetchall()
        known_urls = {url[0] for url in known_urls}

    if "fifteensquared" in source:
        response = requests.get(sitemap_url, headers=headers)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        sitemaps = list(
            reversed(
                [
                    sitemap.text
                    for sitemap in soup.find_all("sitemap")
                    if re.search(
                        r"https://www.fifteensquared.net/wp-sitemap-posts-post-[0-9]*.xml",
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

    elif "bigdave44" in source:
        response = requests.get(sitemap_url, headers=headers)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        sitemaps = list(
            reversed(
                [
                    sitemap.text
                    for sitemap in soup.find_all("loc")
                    if re.search(
                        r"http://bigdave44.com/sitemap-[0-9]*.xml",
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

    elif "times_xwd_times" in source:
        response = requests.get(sitemap_url, headers=headers)
        soup = bs4.BeautifulSoup(response.text, "lxml")
        urls = {url.text for url in soup.find_all("loc")}
        new_urls = list(urls - known_urls)

    return new_urls


if __name__ == "__main__":
    with open("sitemaps.json") as f:
        sitemap_urls = json.load(f)

    for source, sitemap_url in sitemap_urls.items():
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

                with sqlite3.connect("cryptics.sqlite3") as conn:
                    cursor = conn.cursor()
                    sql = f"INSERT INTO html (source, url, html) VALUES (?, ?, ?)"
                    cursor.execute(sql, (source, url, response.text))
                    conn.commit()
            except:
                logging.error(f"Error inserting {url}")

            time.sleep(20)
