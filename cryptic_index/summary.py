import sqlite3


def query_and_print(prompt, sql):
    with sqlite3.connect("cryptics.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute(sql)
        (output,) = cursor.fetchone()
    print(f"\t{prompt.ljust(20)}: {str(output).rjust(7)}")


queries = {
    "bigdave44": [
        ("# crosswords", "select count(1) from raw_bigdave44;"),
        ("# crosswords parsed", "select count(1) from raw_bigdave44 where is_parsed;"),
        (
            "% crosswords parsed",
            "select printf('%.1f', 100.0 * (select count(1) from raw_bigdave44 where is_parsed) / (select count(1) from raw_bigdave44));",
        ),
        ("# clues", "select count(1) from parsed_bigdave44;"),
        (
            "# clues reviewed",
            "select count(1) from parsed_bigdave44 where is_reviewed;",
        ),
        (
            "% clues reviewed",
            "select printf('%.1f', 100.0 * (select count(1) from parsed_bigdave44 where is_reviewed) / (select count(1) from parsed_bigdave44));",
        ),
    ],
    "fifteensquared": [
        ("# crosswords", "select count(1) from raw_fifteensquared;"),
        (
            "# crosswords parsed",
            "select count(1) from raw_fifteensquared where is_parsed;",
        ),
        (
            "% crosswords parsed",
            "select printf('%.1f', 100.0 * (select count(1) from raw_fifteensquared where is_parsed) / (select count(1) from raw_fifteensquared));",
        ),
        ("# clues", "select count(1) from parsed_fifteensquared;"),
        (
            "# clues reviewed",
            "select count(1) from parsed_fifteensquared where is_reviewed;",
        ),
        (
            "% clues reviewed",
            "select printf('%.1f', 100.0 * (select count(1) from parsed_fifteensquared where is_reviewed) / (select count(1) from parsed_fifteensquared));",
        ),
    ],
    "times_xwd_times": [
        ("# crosswords", "select count(1) from raw_times_xwd_times;"),
        (
            "# crosswords parsed",
            "select count(1) from raw_times_xwd_times where is_parsed;",
        ),
        (
            "% crosswords parsed",
            "select printf('%.1f', 100.0 * (select count(1) from raw_times_xwd_times where is_parsed) / (select count(1) from raw_times_xwd_times));",
        ),
        ("# clues", "select count(1) from parsed_times_xwd_times;"),
        (
            "# clues reviewed",
            "select count(1) from parsed_times_xwd_times where is_reviewed;",
        ),
        (
            "% clues reviewed",
            "select printf('%.1f', 100.0 * (select count(1) from parsed_times_xwd_times where is_reviewed) / (select count(1) from parsed_times_xwd_times));",
        ),
    ],
    "cru_cryptics": [
        ("# clues", "select count(1) from parsed_cru_cryptics;"),
        (
            "# clues reviewed",
            "select count(1) from parsed_cru_cryptics where is_reviewed;",
        ),
        (
            "% clues reviewed",
            "select printf('%.1f', 100.0 * (select count(1) from parsed_cru_cryptics where is_reviewed) / (select count(1) from parsed_cru_cryptics));",
        ),
    ],
    "the_browser": [
        ("# clues", "select count(1) from parsed_the_browser;"),
        (
            "# clues reviewed",
            "select count(1) from parsed_the_browser where is_reviewed;",
        ),
        (
            "% clues reviewed",
            "select printf('%.1f', 100.0 * (select count(1) from parsed_the_browser where is_reviewed) / (select count(1) from parsed_the_browser));",
        ),
    ],
    "out_of_left_field": [
        ("# clues", "select count(1) from parsed_out_of_left_field;"),
        (
            "# clues reviewed",
            "select count(1) from parsed_out_of_left_field where is_reviewed;",
        ),
        (
            "% clues reviewed",
            "select printf('%.1f', 100.0 * (select count(1) from parsed_out_of_left_field where is_reviewed) / (select count(1) from parsed_out_of_left_field));",
        ),
    ],
}


for source, queries_ in queries.items():
    print(source)
    for (prompt, query) in queries_:
        query_and_print(prompt, query)
    print()
