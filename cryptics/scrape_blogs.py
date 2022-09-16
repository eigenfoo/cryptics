import json
import logging
import sqlite3
import time

import requests

from cryptics.config import BLOG_SOURCES, HEADERS, SQLITE_DATABASE
from cryptics.utils import get_logger


def scrape_blogs(sources, sleep_interval=20, logger=None):
    if logger is None:
        logger = get_logger()

    for source, get_new_urls_func in sources.items():
        # Get new URLs from the blog
        logger.info(f"Scraping {source}")
        with sqlite3.connect(SQLITE_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT location FROM raw WHERE content_type = 'html' AND source = '{source}';"
            )
            known_urls = {url[0] for url in cursor.fetchall()}
        new_urls = get_new_urls_func(known_urls)
        logger.info(f"Found {len(new_urls)} new urls from {source}")

        # Request new URLs
        for i, url in enumerate(new_urls):
            logger.info(f"Requesting {i}/{len(new_urls)}: {url}")
            response = requests.get(url, headers=HEADERS)
            try:
                if not response.ok:
                    logger.error(f"Response not OK: {url}")
                    continue

                with sqlite3.connect(SQLITE_DATABASE) as conn:
                    cursor = conn.cursor()
                    sql = f"INSERT INTO raw (source, location, content_type, content) VALUES (?, ?, 'html', ?)"
                    cursor.execute(sql, (source, url, response.text))
                    conn.commit()
            except:
                logger.error(f"Error inserting into database: {url}")

            time.sleep(sleep_interval)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    scrape_blogs(sources=BLOG_SOURCES, sleep_interval=1, logger=logger)
