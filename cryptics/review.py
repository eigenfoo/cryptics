from __future__ import annotations

import argparse
import json
import os
import random
import readline
import sqlite3

from cryptics.config import SQLITE_DATABASE

parser = argparse.ArgumentParser()
parser.add_argument("--rowid", type=str, nargs="?", default=None)
parser.add_argument("--source", type=str, nargs="?", default="times_xwd_times")
parser.add_argument("--where", type=str, default="NOT coalesce(is_reviewed, 0)")
args = parser.parse_args()


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


if os.path.exists("todo.txt"):
    with open("todo.txt", "r") as f:
        todo_rowids: list[str] | None = f.read().split()
elif args.rowid:
    todo_rowids = [args.rowid]
else:
    todo_rowids = None


while True:
    os.system("cls" if os.name == "nt" else "clear")
    print(2 * "\n")
    with sqlite3.connect(SQLITE_DATABASE) as conn:
        if todo_rowids is not None:
            sql = f"SELECT * FROM clues WHERE rowid = '{todo_rowids.pop(0)}';"
        else:
            sql = f"SELECT * FROM clues WHERE source = '{args.source}' AND {args.where} ORDER BY RANDOM() LIMIT 1;"

        cursor = conn.cursor()
        cursor.execute(sql)
        (
            row_id,
            source,
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

    print(f"{Colors.YELLOW}             {args.source}/{row_id}{Colors.ENDC}")
    print()
    print(f"{Colors.CYAN}Puzzle Name:{Colors.ENDC} {puzzle_name}")
    print(f"{Colors.CYAN}Puzzle Date:{Colors.ENDC} {puzzle_date}")
    print(f"{Colors.CYAN}Clue Number:{Colors.ENDC} {clue_number}")
    print()
    print(f"{Colors.CYAN}       Clue:{Colors.ENDC} {clue}")
    print()

    print(f"{Colors.CYAN}     Answer:{Colors.ENDC} {answer}")
    print()
    print(f"{Colors.CYAN} Definition:{Colors.ENDC} {definition}")
    print(f"{Colors.CYAN} Annotation:{Colors.ENDC} {annotation}")
    print()
    print(f"{Colors.CYAN} Puzzle URL:{Colors.ENDC} {puzzle_url}")
    print(f"{Colors.CYAN} Source URL:{Colors.ENDC} {source_url}")

    print()
    print(
        f"             Press {Colors.RED}e{Colors.ENDC} to edit, {Colors.RED}d{Colors.ENDC} to delete, {Colors.RED}s{Colors.ENDC} to skip, or {Colors.GREEN}Enter{Colors.ENDC} for another clue."
    )
    user_input = input()

    if user_input.strip() == "e":
        clue = maybe_edit("       Clue", clue)
        answer = maybe_edit("     Answer", answer)
        definition = maybe_edit(" Definition", definition)
        annotation = maybe_edit(" Annotation", annotation)
        clue_number = maybe_edit("Clue Number", clue_number)
        with sqlite3.connect(SQLITE_DATABASE) as conn:
            cursor = conn.cursor()
            sql = f"""
            UPDATE clues
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
        with sqlite3.connect(SQLITE_DATABASE) as conn:
            cursor = conn.cursor()
            sql = f"""
            DELETE FROM clues
            WHERE rowid = ?;
            """
            cursor.execute(sql, (row_id,))
        continue  # Row is deleted; don't update is_reviewed
    elif user_input.strip() == "s":
        continue

    with sqlite3.connect(SQLITE_DATABASE) as conn:
        cursor = conn.cursor()
        sql = f"""
        UPDATE clues
        SET is_reviewed = True,
            datetime_reviewed = datetime("now")
        WHERE rowid = ?;
        """
        cursor.execute(sql, (row_id,))

    if os.path.exists("todo.txt"):
        # Delete first line of todo.txt
        with open("todo.txt", "r") as f:
            data = f.read().splitlines(True)
        with open("todo.txt", "w") as f:
            f.writelines(data[1:])
