import json
import logging
import sqlite3
import time

import requests

from cryptics.config import BLOG_SOURCES, HEADERS, SQLITE_DATABASE


logging.basicConfig(level=logging.INFO)


def scrape_blogs(sources, sleep_interval=1):
    for source, get_new_urls_func in sources.items():
        # Get new URLs from the blog
        logging.info(f"Populating from {source}...")
        with sqlite3.connect(SQLITE_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT location FROM raw WHERE content_type = 'html' AND source = '{source}';")
            known_urls = {url[0] for url in cursor.fetchall()}
        new_urls = get_new_urls_func(known_urls)
        logging.info(f"Found {len(new_urls)} new urls.")

        # Scrape new URLs
        for i, url in enumerate(new_urls):
            logging.info(f"{i} / {len(new_urls)}:\t{url}")
            response = requests.get(url, headers=HEADERS)
            try:
                if not response.ok:
                    logging.error(f"Response not OK for {url}")
                    continue

                with sqlite3.connect(SQLITE_DATABASE) as conn:
                    cursor = conn.cursor()
                    sql = f"INSERT INTO raw (source, location, content_type, content) VALUES (?, ?, 'html', ?)"
                    cursor.execute(sql, (source, url, response.text))
                    conn.commit()
            except:
                logging.error(f"Error inserting {url}")

            time.sleep(sleep_interval)


if __name__ == "__main__":
    scrape_blogs(sources=BLOG_SOURCES)
