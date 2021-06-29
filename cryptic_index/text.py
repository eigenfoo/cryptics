import re
import string

import bs4
import pandas as pd
from cryptic_index.tables import extract_definitions


def is_parsable_text_type_1(response):
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    asset_body = soup.find("div", attrs={"class": "asset-body"})
    for br in asset_body.find_all("br"):
        br.replace_with("\n")

    if not 20 <= len(asset_body.find_all("u")) <= 40:
        return False

    for tag in asset_body.find_all():
        tag.extract()

    if not 100 <= len(asset_body):
        return False

    return True


def parse_text_type_1(response):
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    asset_body = soup.find("div", attrs={"class": "asset-body"})
    # if asset_body is None:
    #     asset_body = soup.find("article")
    for br in asset_body.find_all("br"):
        br.replace_with("\n")

    # Get rid of preamble
    lines = [line.strip() for line in asset_body.text.splitlines() if line.strip()]
    while lines[0].lower() not in ["across", "down"]:
        lines.pop(0)

    annotations = []
    answers = []
    clues = []
    clue_numbers = []

    while lines:
        if lines[0].lower() in ["across", "down"]:
            clue_direction = lines.pop(0)
            clue_direction = "a" if clue_direction.lower() == "across" else "d"
        else:
            line_1 = lines.pop(0)
            line_2 = lines.pop(0)

            clue_number, clue = line_1.split(maxsplit=1)
            match = re.search("^[A-Z ]*", line_2)
            answer = line_2[: match.end()].strip()
            annotation = line_2[match.end() :].strip(
                string.whitespace + string.punctuation
            )

            clue_numbers.append(clue_number.strip(string.punctuation) + clue_direction)
            clues.append(clue)
            answers.append(answer)
            annotations.append(annotation)

    definitions = extract_definitions(asset_body, clues, 2)

    table = pd.DataFrame([clue_numbers, clues, definitions, answers, annotations]).T
    table.columns = ["clue_number", "clue", "definition", "answer", "annotation"]

    return table
