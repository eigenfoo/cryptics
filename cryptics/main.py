import argparse
import json
import logging
import sqlite3
from datetime import datetime
from typing import List

from cryptics.parse import try_parse
from cryptics.populate_db import populate_db


def parse_unparsed_html(sources: List[str], datetime_requested: str):
    for source in sources:
        with sqlite3.connect("cryptics.sqlite3") as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT url FROM html WHERE source = '{source}' AND NOT is_parsed AND datetime_requested >= '{datetime_requested}';"
            )
            urls = [url for url, in cursor.fetchall()]

        for i, url in enumerate(urls):
            with sqlite3.connect("cryptics.sqlite3") as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT html FROM html WHERE url = '{url}';")
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
            with sqlite3.connect("cryptics.sqlite3") as conn:
                data.to_sql(f"clues", conn, if_exists="append", index=False)

                cursor = conn.cursor()
                sql = f"UPDATE html SET is_parsed = TRUE, datetime_parsed = datetime('now') WHERE url = '{url}';"
                cursor.execute(sql)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sleep-interval", type=int)
    parser.add_argument(
        "--datetime-requested", type=str, default=datetime.now().strftime("%Y-%m-%d")
    )
    args = parser.parse_args()

    with open("sitemaps.json") as f:
        sources = json.load(f).keys()

    populate_db(sleep_interval=args.sleep_interval)
    parse_unparsed_html(sources=sources, datetime_requested=args.datetime_requested)
