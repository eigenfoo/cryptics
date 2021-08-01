import os
import sqlite3
import readline


POST = "times_xwd_times"
TRAIN = False


class TerminalColors:
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

    print(f"{TerminalColors.YELLOW}{row_id}{TerminalColors.ENDC}")
    print()
    print(f"{TerminalColors.CYAN}       Clue:{TerminalColors.ENDC} {clue}")
    print()
    if TRAIN:
        print("\t\tPress Enter to reveal answer")
        print()
        _ = input()
    print(f"{TerminalColors.CYAN}     Answer:{TerminalColors.ENDC} {answer}")
    print()
    if TRAIN:
        print("\t\tPress Enter for definition, annotation and metadata")
        print()
        _ = input()
    print(f"{TerminalColors.CYAN} Definition:{TerminalColors.ENDC} {definition}")
    print(f"{TerminalColors.CYAN} Annotation:{TerminalColors.ENDC} {annotation}")
    print()
    print(f"{TerminalColors.CYAN}Clue Number:{TerminalColors.ENDC} {clue_number}")
    print(f"{TerminalColors.CYAN}Puzzle Date:{TerminalColors.ENDC} {puzzle_date}")
    print(f"{TerminalColors.CYAN}Puzzle Name:{TerminalColors.ENDC} {puzzle_name}")
    print(f"{TerminalColors.CYAN} Puzzle URL:{TerminalColors.ENDC} {puzzle_url}")
    print(f"{TerminalColors.CYAN} Source URL:{TerminalColors.ENDC} {source_url}")
    print()
    print("\t\tEnter `e` to edit, `d` to delete, or Enter for another clue")
    print()
    user_input = input()

    if user_input.strip() == "e":
        clue = maybe_edit(
            f"{TerminalColors.GREEN}       Clue{TerminalColors.ENDC}", clue
        )
        answer = maybe_edit(
            f"{TerminalColors.GREEN}     Answer{TerminalColors.ENDC}", answer
        )
        definition = maybe_edit(
            f"{TerminalColors.GREEN} Definition{TerminalColors.ENDC}", definition
        )
        annotation = maybe_edit(
            f"{TerminalColors.GREEN} Annotation{TerminalColors.ENDC}", annotation
        )
        clue_number = maybe_edit(
            f"{TerminalColors.GREEN}Clue Number{TerminalColors.ENDC}", clue_number
        )
        puzzle_date = maybe_edit(
            f"{TerminalColors.GREEN}Puzzle Date{TerminalColors.ENDC}", puzzle_date
        )
        puzzle_name = maybe_edit(
            f"{TerminalColors.GREEN}Puzzle Name{TerminalColors.ENDC}", puzzle_name
        )
        puzzle_url = maybe_edit(
            f"{TerminalColors.GREEN} Puzzle URL{TerminalColors.ENDC}", puzzle_url
        )
        source_url = maybe_edit(
            f"{TerminalColors.GREEN} Source URL{TerminalColors.ENDC}", source_url
        )
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
