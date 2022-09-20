from __future__ import annotations

import argparse
import json
import logging
import sqlite3
from datetime import datetime
from typing import Any, Callable, List

from cryptics.config import BLOG_SOURCES, SQLITE_DATABASE
from cryptics.parse import try_parse
from cryptics.scrape_blogs import scrape_blogs
from cryptics.utils import get_logger


def parse_unparsed_html(
    sources: dict[str, Callable[[Any], Any]],
    datetime_requested: str,
    logger: logging.Logger | None = None,
):
    if logger is None:
        logger = get_logger()

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
                logger.info(f"Parsing {i}/{len(urls)}: {url}")
                data = try_parse(html, url)
            except:
                logger.error(f"Failed to parse: {url}", exc_info=True)

            if data is None:
                logger.error(f"Parse returned None: {url}")
                continue

            data["source"] = source
            with sqlite3.connect(SQLITE_DATABASE) as conn:
                data.to_sql(f"clues", conn, if_exists="append", index=False)

                cursor = conn.cursor()
                sql = f"UPDATE raw SET is_parsed = TRUE, datetime_parsed = datetime('now') WHERE location = '{url}';"
                cursor.execute(sql)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)

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
        sources=BLOG_SOURCES, datetime_requested=args.datetime_requested, logger=logger
    )
