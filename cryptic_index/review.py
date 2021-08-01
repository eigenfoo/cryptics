import os
import readline
import sqlite3
import time


POST = "bigdave44"
TRAIN = False


class Colors:
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"


def prefilled_input(prompt, prefill=""):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()


def maybe_edit(field, current_value):
    new_value = prefilled_input(field + ": ", prefill=current_value)
    if new_value.strip():
        return new_value
    else:
        return current_value


os.system("cls" if os.name == "nt" else "clear")
print(10 * "\n")
print("             Welcome!")
print()
time.sleep(1)
print(f"             Serving clues indexed from {Colors.RED}{POST}{Colors.ENDC}...")
time.sleep(1)

while True:
    os.system("cls" if os.name == "nt" else "clear")
    print(2 * "\n")
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

    print(f"{Colors.YELLOW}             {row_id}{Colors.ENDC}")
    print()
    print(f"{Colors.CYAN}       Clue:{Colors.ENDC} {clue}")
    print()
    if TRAIN:
        print(f"             Press {Colors.GREEN}Enter{Colors.ENDC} to reveal answer.")
        print()
        _ = input()
    print(f"{Colors.CYAN}     Answer:{Colors.ENDC} {answer}")
    print()
    if TRAIN:
        print(
            f"             Press {Colors.GREEN}Enter{Colors.ENDC} for definition, annotation and metadata."
        )
        print()
        _ = input()
    print(f"{Colors.CYAN} Definition:{Colors.ENDC} {definition}")
    print(f"{Colors.CYAN} Annotation:{Colors.ENDC} {annotation}")
    print()
    print(f"{Colors.CYAN}Clue Number:{Colors.ENDC} {clue_number}")
    print(f"{Colors.CYAN}Puzzle Date:{Colors.ENDC} {puzzle_date}")
    print(f"{Colors.CYAN}Puzzle Name:{Colors.ENDC} {puzzle_name}")
    print(f"{Colors.CYAN} Puzzle URL:{Colors.ENDC} {puzzle_url}")
    print(f"{Colors.CYAN} Source URL:{Colors.ENDC} {source_url}")
    print()
    print(
        f"             Press {Colors.RED}e{Colors.ENDC} to edit, {Colors.RED}d{Colors.ENDC} to delete, {Colors.RED}s{Colors.ENDC} to skip, or {Colors.GREEN}Enter{Colors.ENDC} for another clue."
    )
    print()
    user_input = input()

    if user_input.strip() == "e":
        clue = maybe_edit(f"       Clue", clue)
        answer = maybe_edit(f"     Answer", answer)
        definition = maybe_edit(f" Definition", definition)
        annotation = maybe_edit(f" Annotation", annotation)
        clue_number = maybe_edit(f"Clue Number", clue_number)
        puzzle_date = maybe_edit(f"Puzzle Date", puzzle_date)
        puzzle_name = maybe_edit(f"Puzzle Name", puzzle_name)
        puzzle_url = maybe_edit(f" Puzzle URL", puzzle_url)
        source_url = maybe_edit(f" Source URL", source_url)
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
    elif user_input.strip() == "s":
        continue

    with sqlite3.connect("cryptics.sqlite3") as conn:
        cursor = conn.cursor()
        sql = f"""
        UPDATE parsed_{POST}
        SET is_reviewed = True,
            datetime_reviewed = datetime("now")
        WHERE rowid = ?;
        """
        cursor.execute(sql, (row_id,))
