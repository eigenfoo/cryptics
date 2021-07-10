import os
import sqlite3
import readline


POST = "bigdave44"


def rlinput(prompt, prefill=""):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()


def maybe_edit(field, current_value):
    new_value = rlinput(field + ": ", prefill=current_value)
    if new_value.strip():
        return new_value
    else:
        return current_value


while True:
    os.system("cls" if os.name == "nt" else "clear")
    print(5 * "\n")

    with sqlite3.connect("cryptics.sqlite3") as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT rowid, * FROM parsed_{POST} WHERE NOT is_reviewed ORDER BY RANDOM() LIMIT 1;")
        (
            row_id,
            clue,
            answer,
            definition,
            annotation,
            clue_number,
            puzzle_date,
            puzzle_name,
            puzzle_url,
            source_url,
            _,
            _,
        ) = cursor.fetchone()

    print(f"{row_id}")
    print()
    print(clue)
    print(f"     Answer: {answer}")
    print()
    print(f" Definition: {definition}")
    print(f" Annotation: {annotation}")
    print()
    print(f"Clue Number: {clue_number}")
    print(f"Puzzle Date: {puzzle_date}")
    print(f"Puzzle Name: {puzzle_name}")
    print(f" Puzzle URL: {puzzle_url}")
    print(f" Source URL: {source_url}")
    print()
    print("\n\tEnter `e` to edit, or any other characters for another clue\n")
    user_input = input()

    if user_input.strip() == "e":
        clue = maybe_edit("Clue", clue)
        answer = maybe_edit("Answer", answer)
        definition = maybe_edit("Definition", definition)
        annotation = maybe_edit("Annotation", annotation)
        clue_number = maybe_edit("Clue Number", clue_number)
        puzzle_date = maybe_edit("Puzzle Date", puzzle_date)
        puzzle_name = maybe_edit("Puzzle Name", puzzle_name)
        puzzle_url = maybe_edit("Puzzle URL", puzzle_url)
        source_url = maybe_edit("Source URL", source_url)

        with sqlite3.connect("cryptics.sqlite3") as conn:
            cursor = conn.cursor()
            sql = f"""
            UPDATE parsed_{POST}
            SET clue = '{clue}',
                answer = '{answer}',
                definition = '{definition}',
                annotation = '{annotation}',
                clue_number = '{clue_number}',
                puzzle_date = '{puzzle_date}',
                puzzle_name = '{puzzle_name}',
                puzzle_url = '{puzzle_url}',
                source_url = '{source_url}',
                is_reviewed = True,
                datetime_reviewed = datetime('now')
            WHERE rowid = {row_id};
            """
            cursor.execute(sql)
