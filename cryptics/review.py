import argparse
import json
import os
import random
import readline
import sqlite3

from cryptics.config import SQLITE_DATABASE


parser = argparse.ArgumentParser()
parser.add_argument("--source", type=str, nargs="?", default="times_xwd_times")
parser.add_argument("--train", dest="train", action="store_true")
parser.add_argument("--no-train", dest="train", action="store_false")
parser.set_defaults(train=False)
parser.add_argument(
    "--where", type=str, default="NOT is_reviewed"
)
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


def maybe_give_hints(answer):
    answer = answer.upper().strip().replace(" ", "").replace("-", "")
    user_input = input()
    to_show = len(answer) * "."
    i = round(random.random())
    while user_input.lower().strip() == "l":
        if i >= len(answer):
            break
        to_show = to_show[0:i] + answer[i] + to_show[i + 1 :]
        i += 2
        print(f"       {Colors.CYAN}Hint:{Colors.ENDC} {to_show}")
        user_input = input()


if args.train:
    os.system("cls" if os.name == "nt" else "clear")
    print(2 * "\n")
    players = input(
        f"{Colors.RED}             Who's playing? Enter names separated by spaces.\n              > {Colors.ENDC}"
    )
    players = players.split()
    with open("scores.json", "r") as f:
        scores = json.load(f)
else:
    if os.path.exists("todo.txt"):
        with open("todo.txt", "r") as f:
            todo_rowids = f.read().split()
    else:
        todo_rowids = None


while True:
    os.system("cls" if os.name == "nt" else "clear")
    print(2 * "\n")
    with sqlite3.connect(SQLITE_DATABASE) as conn:
        if not args.train and todo_rowids is not None:
            sql = f"SELECT rowid, * FROM clues WHERE rowid = '{todo_rowids.pop(0)}';"
        else:
            sql = f"SELECT rowid, * FROM clues WHERE source = '{args.source}' AND {args.where} ORDER BY RANDOM() LIMIT 1;"

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

    if args.train:
        for player in players:
            a, b = scores[player]
            print(
                70 * " "
                + f"{Colors.RED}{player.title().rjust(10)} {a} / {b} ({a / b:.2f}){Colors.ENDC}"
            )

    print(f"{Colors.YELLOW}             {args.source}/{row_id}{Colors.ENDC}")
    print()
    print(f"{Colors.CYAN}Puzzle Name:{Colors.ENDC} {puzzle_name}")
    print(f"{Colors.CYAN}Puzzle Date:{Colors.ENDC} {puzzle_date}")
    print(f"{Colors.CYAN}Clue Number:{Colors.ENDC} {clue_number}")
    print()
    print(f"{Colors.CYAN}       Clue:{Colors.ENDC} {clue}")
    print()
    if args.train:
        print(
            f"             Press {Colors.RED}l{Colors.ENDC} to reveal a letter or {Colors.GREEN}Enter{Colors.ENDC} to reveal answer."
        )
        maybe_give_hints(answer)

    print(f"{Colors.CYAN}     Answer:{Colors.ENDC} {answer}")
    print()
    if args.train:
        print(
            f"             Press {Colors.GREEN}Enter{Colors.ENDC} for definition, annotation and URLs."
        )
        _ = input()
    print(f"{Colors.CYAN} Definition:{Colors.ENDC} {definition}")
    print(f"{Colors.CYAN} Annotation:{Colors.ENDC} {annotation}")
    print()
    print(f"{Colors.CYAN} Puzzle URL:{Colors.ENDC} {puzzle_url}")
    print(f"{Colors.CYAN} Source URL:{Colors.ENDC} {source_url}")

    if args.train:
        print()
        winners = input(
            f"{Colors.RED}             So, who got that one right?\n              > {Colors.ENDC}"
        )
        print()
        winners = winners.split()
        losers = set(players) - set(winners)
        for winner in winners:
            if player in scores.keys():
                a, b = scores[winner]
                scores[winner] = (a + 1, b + 1)
                print(
                    f"{Colors.RED}             Congrats, {winner.title()}!{Colors.ENDC}"
                )
        for loser in losers:
            if loser in scores.keys():
                a, b = scores[loser]
                scores[loser] = (a, b + 1)
                print(f"{Colors.RED}             Oof, {loser.title()}...{Colors.ENDC}")
        with open("scores.json", "w") as f:
            json.dump(scores, f)

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

    if not args.train and os.path.exists("todo.txt"):
        # Delete first line of todo.txt
        with open("todo.txt", "r") as f:
            data = f.read().splitlines(True)
        with open("todo.txt", "w") as f:
            f.writelines(data[1:])
