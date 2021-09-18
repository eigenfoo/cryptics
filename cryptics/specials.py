import re

import pandas as pd
import bs4

from cryptics.utils import extract_definitions


DASHES = ["-", "—", "–", "–", "—"]
PUNCTUATION_IN_ANNOTATION = DASHES + list("{}~*/\\")
PUNCTUATION_IN_ANSWERS = DASHES + list("(){}|~*/\\_")


def delete_chars(s, chars):
    for char in chars:
        s = s.replace(char, "")
    return s


def is_parsable_special_type_1(html):
    soup = bs4.BeautifulSoup(html, "html.parser")
    entry_content = soup.find("div", attrs={"class": lambda s: s in ["entry-content"]})
    answers_and_annotations = [
        line for line in entry_content.text.split("\n") if line.strip()
    ]

    phrases = [
        "cox",
        "rathvon",
        "signing off for today",
        "falcon",
        "key to reference sources",
    ]

    return (
        30 <= len(entry_content.find_all("table"))
        and 100 <= len(answers_and_annotations)
        and 3 <= sum([phrase in entry_content.text.lower() for phrase in phrases])
    )


def parse_special_type_1(html):
    soup = bs4.BeautifulSoup(html, "html.parser")
    entry_content = soup.find("div", attrs={"class": lambda s: s in ["entry-content"]})

    clue_number_and_clues = [a.text for a in entry_content.find_all("table")]

    clue_numbers = []
    clues = []
    for line in clue_number_and_clues:
        clue_number = re.search(r"^[0-9]+[a|d]?", line)
        if clue_number is None:
            continue
        clue = line[clue_number.end() :].replace("\n", " ").strip()

        clue_numbers.append(clue_number.group())
        clues.append(delete_chars(clue, PUNCTUATION_IN_ANNOTATION))

    # Save this for later - before we extract all the tables.
    raw_definitions = [
        tag for table in entry_content.find_all("table") for tag in table.find_all("u")
    ]

    for table in entry_content.find_all("table"):
        table.extract()

    stop_phrases = ["introduction", "epilogue", "signing off for today"]
    answers_and_annotations = [
        line
        for line in entry_content.text.split("\n")
        if line.strip()
        and not any(
            line.lower().startswith(stop_phrase) for stop_phrase in stop_phrases
        )
    ]

    answers = []
    annotations = []
    for line in answers_and_annotations:
        try:
            divider = re.search("\s+[" + "|".join(DASHES) + "]\s+", line)
            answer = line[: divider.start()]
            annotation = line[divider.end() :]
            if not any([c.isalpha() for c in answer]):
                continue
        except AttributeError:
            continue

        answers.append(delete_chars(answer, PUNCTUATION_IN_ANSWERS))
        annotations.append(annotation.strip("".join(PUNCTUATION_IN_ANNOTATION + [" "])))

    definitions = extract_definitions(soup, clues, raw_definitions=raw_definitions)

    return pd.DataFrame(
        data=[clue_numbers, answers, clues, annotations, definitions],
        index=["clue_number", "answer", "clue", "annotation", "definition"],
    ).T
