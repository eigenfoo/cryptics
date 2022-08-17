import argparse
import json
import logging
import sqlite3
from datetime import datetime
from typing import List

from cryptics.parse import try_parse
from cryptics.scrape_blogs import scrape_blogs
from cryptics.config import BLOG_SOURCES, SQLITE_DATABASE


def parse_unparsed_html(sources: List[str], datetime_requested: str):
    for source in sources:
        with sqlite3.connect(SQLITE_DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT location FROM raw WHERE content_type = 'html' AND source = '{source}' AND NOT is_parsed AND datetime_requested >= '{datetime_requested}';"
            )
            urls = [url for url, in cursor.fetchall()]

        for i, url in enumerate(urls):
            with sqlite3.connect(SQLITE_DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT content FROM raw WHERE location = '{url}';")
                (html,) = cursor.fetchone()

            data = None
            try:
                logging.info(f"{i} / {len(urls)}\t" + url)
                data = try_parse(html, url)
            except:
                pass

            if data is None:
                logging.warning("Failed.")
                continue

            logging.info("Success!")

            data["source"] = source
            with sqlite3.connect(SQLITE_DATABASE) as conn:
                data.to_sql(f"clues", conn, if_exists="append", index=False)

                cursor = conn.cursor()
                sql = f"UPDATE raw SET is_parsed = TRUE, datetime_parsed = datetime('now') WHERE location = '{url}';"
                cursor.execute(sql)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--scrape", dest="scrape", action="store_true")
    parser.add_argument("--no-scrape", dest="scrape", action="store_false")
    parser.set_defaults(scrape=True)
    parser.add_argument("--sleep-interval", type=int, default=20)
    parser.add_argument(
        "--datetime-requested", type=str, default=datetime.now().strftime("%Y-%m-%d")
    )
    args = parser.parse_args()

    if args.scrape:
        scrape_blogs(sources=BLOG_SOURCES, sleep_interval=args.sleep_interval)

    parse_unparsed_html(
        sources=BLOG_SOURCES, datetime_requested=args.datetime_requested
    )
