import json
import sqlite3
from cryptics.parse import try_parse


with open("sitemaps.json") as f:
    sources = json.load(f).keys()


for source in sources:
    with sqlite3.connect("cryptics.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT url FROM html WHERE source = '{source}' AND NOT is_parsed AND datetime_requested >= '2021-09-04';")
        urls = [url for url, in cursor.fetchall()]

    for i, url in enumerate(urls):
        with sqlite3.connect("cryptics.sqlite3") as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT html FROM html WHERE url = '{url}';")
            (html,) = cursor.fetchone()

        data = None
        try:
            print(f"{i} / {len(urls)}", url)
            data = try_parse(html, url)
        except:
            pass

        if data is None:
            print("\tFailed.")
            continue

        print("\tSuccess!")

        data["source"] = source
        with sqlite3.connect("cryptics.sqlite3") as conn:
            data.to_sql(f"clues", conn, if_exists="append", index=False)

            cursor = conn.cursor()
            sql = f"UPDATE html SET is_parsed = TRUE, datetime_parsed = datetime('now') WHERE url = '{url}';"
            cursor.execute(sql)
