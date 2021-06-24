import datetime
import json
import logging
import re
import sqlite3
import time

import requests
import bs4

SITEMAP_URL = "https://www.fifteensquared.net/wp-sitemap.xml"

logging.basicConfig(level=logging.INFO)
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "Accept-Encoding": "gzip",
}


with sqlite3.connect("cryptics.sqlite3") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM fifteensquared;")
    known_urls = cursor.fetchall()
    known_urls = {url[0] for url in known_urls}

response = requests.get(SITEMAP_URL, headers=headers)
soup = bs4.BeautifulSoup(response.text, "lxml")

# FIXME: just 10 for now...
sitemaps = list(
    reversed(
        [
            sitemap.text
            for sitemap in soup.find_all("sitemap")
            if re.search(
                r"https://www.fifteensquared.net/wp-sitemap-posts-post-10.xml",
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

logging.info(f"Found {len(new_urls)} new urls.")

for i, url in enumerate(new_urls):
    logging.info(f"{i} / {len(new_urls)}:\t{url}")
    response = requests.get(url, headers=headers)

    try:
        if response.ok:
            with sqlite3.connect("cryptics.sqlite3") as conn:
                cursor = conn.cursor()
                sql = "INSERT INTO fifteensquared (url, html) VALUES (?, ?)"
                cursor.execute(sql, (url, response.text))
                conn.commit()
        else:
            logging.error(f"Response not OK for {url}")
    except:
        logging.error(f"Error inserting {url}")

    time.sleep(20)
