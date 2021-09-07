import sqlite3


def query_and_print(prompt, sql):
    with sqlite3.connect("cryptics.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        (output,) = cursor.fetchone()
    print(f"\t{prompt.ljust(20)}: {str(output).rjust(7)}")


if __name__ == "__main__":
    with sqlite3.connect("cryptics.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT source FROM clues;")
        sources = sorted([source for (source,) in cursor.fetchall()])

    queries = {
        source: [
            ("# crosswords", f"SELECT count(1) FROM html WHERE source = '{source}';"),
            (
                "# crosswords parsed",
                f"SELECT count(1) FROM html WHERE source = '{source}' AND is_parsed;",
            ),
            (
                "% crosswords parsed",
                f"SELECT printf('%.1f', 100.0 * (SELECT count(1) FROM html WHERE source = '{source}' AND is_parsed) / (SELECT count(1) FROM html WHERE source = '{source}'));",
            ),
            ("# clues", f"SELECT count(1) FROM clues WHERE source = '{source}';"),
            (
                "# clues reviewed",
                f"SELECT count(1) FROM clues WHERE source = '{source}' AND is_reviewed;",
            ),
            (
                "% clues reviewed",
                f"SELECT printf('%.1f', 100.0 * (SELECT count(1) FROM clues WHERE source = '{source}' AND is_reviewed) / (SELECT count(1) FROM clues WHERE source = '{source}'));",
            ),
        ]
        for source in sources
    }

    for source, queries_ in queries.items():
        print(source)
        for (prompt, query) in queries_:
            query_and_print(prompt, query)
        print()
