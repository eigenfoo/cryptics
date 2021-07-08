import sqlite3
from cryptic_index.parse import try_parse


POST = "times_xwd_times"

with sqlite3.connect("cryptics.sqlite3") as conn:
    cursor = conn.cursor()
    cursor.execute(f"SELECT url FROM raw_{POST} WHERE NOT is_parsed;")
    urls = [url for url, in cursor.fetchall()]


for i, url in enumerate(urls):
    with sqlite3.connect("cryptics.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT html FROM raw_{POST} WHERE url = '{url}';")
        (html,) = cursor.fetchone()

    try:
        print(f"{i} / {len(urls)}", url)
        data = try_parse(html, url)
    except:
        pass

    if data is None:
        print("\tFailed.")
        continue

    print("\tSuccess!")
    with sqlite3.connect("cryptics.sqlite3") as conn:
        data.to_sql(f"parsed_{POST}", conn, if_exists="append", index=False)

        cursor = conn.cursor()
        sql = f"UPDATE raw_{POST} SET is_parsed = TRUE, datetime_parsed = datetime('now') WHERE url = '{url}';"
        cursor.execute(sql)