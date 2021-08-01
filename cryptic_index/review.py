import os
import sqlite3
import readline


POST = "times_xwd_times"
TRAIN = True


class colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'


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
        cursor.execute(
            f"SELECT rowid, * FROM parsed_{POST} WHERE NOT is_reviewed ORDER BY RANDOM() LIMIT 1;"
        )
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

    print(f"{colors.YELLOW}{row_id}{colors.ENDC}")
    print()
    print(f"{colors.CYAN}       Clue:{colors.ENDC} {clue}")
    print()
    if TRAIN:
        print("\t\tPress Enter to reveal answer")
        print()
        _ = input()
    print(f"{colors.CYAN}     Answer:{colors.ENDC} {answer}")
    print()
    if TRAIN:
        print("\t\tPress Enter for definition, annotation and metadata")
        print()
        _ = input()
    print(f"{colors.CYAN} Definition:{colors.ENDC} {definition}")
    print(f"{colors.CYAN} Annotation:{colors.ENDC} {annotation}")
    print()
    print(f"{colors.CYAN}Clue Number:{colors.ENDC} {clue_number}")
    print(f"{colors.CYAN}Puzzle Date:{colors.ENDC} {puzzle_date}")
    print(f"{colors.CYAN}Puzzle Name:{colors.ENDC} {puzzle_name}")
    print(f"{colors.CYAN} Puzzle URL:{colors.ENDC} {puzzle_url}")
    print(f"{colors.CYAN} Source URL:{colors.ENDC} {source_url}")
    print()
    print("\t\tEnter `e` to edit, `d` to delete, or Enter for another clue")
    print()
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
            SET clue = ?,
                answer = ?,
                definition = ?,
                annotation = ?,
                clue_number = ?,
                puzzle_date = ?,
                puzzle_name = ?,
                puzzle_url = ?,
                source_url = ?
            WHERE rowid = ?;
            """
            cursor.execute(
                sql,
                (
                    clue,
                    answer,
                    definition,
                    annotation,
                    clue_number,
                    puzzle_date,
                    puzzle_name,
                    puzzle_url,
                    source_url,
                    row_id,
                ),
            )
    elif user_input.strip() == "d":
        with sqlite3.connect("cryptics.sqlite3") as conn:
            cursor = conn.cursor()
            sql = f"""
            DELETE FROM parsed_{POST}
            WHERE rowid = ?;
            """
            cursor.execute(sql, (row_id,))
            continue  # Row is deleted; don't update is_reviewed

    with sqlite3.connect("cryptics.sqlite3") as conn:
        cursor = conn.cursor()
        sql = f"""
        UPDATE parsed_{POST}
        SET is_reviewed = True,
            datetime_reviewed = datetime("now")
        WHERE rowid = ?;
        """
        cursor.execute(sql, (row_id,))
