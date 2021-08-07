import re
import string

import bs4
import pandas as pd
from cryptic_index.tables import extract_definitions


def is_parsable_text_type_1(html):
    """
    Identifies if the text looks something like this:

    ACROSS

    1	Dad, to irritate, gets into row about mending equipment (6,3)
    REPAIR KIT - PA IRK in TIER reversed
    6	Carbon copies for heads (5)
    CAPES - C APES; geographical heads (promontories)
                        ...

    DOWN

    1	Holy object oddly laid in playing field (5)
    RELIC - L[a]I[d] in REC
    2	Sweet complexion(7,3,5)
    PEACHES AND CREAM - DD
                        ...
    """
    soup = bs4.BeautifulSoup(html, "html.parser")
    asset_body = soup.find(
        "div", attrs={"class": lambda s: s in ["asset-body", "entry-content"]}
    )
    for br in asset_body.find_all("br"):
        br.replace_with("\n")

    return (
        # At least 20 underlined entries (definitions)
        20
        <= len(
            asset_body.find_all("u")
            + asset_body.find_all(
                "span", attrs={"style": re.compile("underline|color")}
            )
        )
        # At least 20 "ANSWER - annotation" lines
        and (
            20 <= len(re.findall(r"\s+[A-Z ]+\s*[-|—|–|–|:]\s+", asset_body.text))
            or 20 <= len(re.findall(r"\s+\{[A-Z ]+\}\s*", asset_body.text))
        )
        # At least 20 "123a. clue goes here (123)" lines
        and 20
        <= len(re.findall(r"\s+[0-9]+[a|d]?\.?\s+.*\([0-9, ]+\)", asset_body.text))
    )


def parse_text_type_1(html):
    soup = bs4.BeautifulSoup(html, "html.parser")
    asset_body = soup.find(
        "div", attrs={"class": lambda s: s in ["asset-body", "entry-content"]}
    )
    for br in asset_body.find_all("br"):
        br.replace_with("\n")

    lines = [line.strip() for line in asset_body.text.splitlines() if line.strip()]
    # Get rid of preamble
    while all([s not in lines[0].lower() for s in ["across", "down"]]):
        lines.pop(0)

    annotations = []
    answers = []
    clues = []
    clue_numbers = []

    while lines:
        line_1 = None
        line_2 = None

        if lines[0].strip(string.whitespace + "\ufeff") == "":
            lines.pop(0)
        elif lines[0].lower() in ["across", "down"]:
            clue_direction = lines.pop(0)
            clue_direction = "a" if "across" in clue_direction.lower() else "d"
        else:
            try:
                line_1 = lines.pop(0)
                line_2 = lines.pop(0)

                clue_number, clue = line_1.split(maxsplit=1)
                if not re.search(r"[0-9]+[a|d]?", clue_number.strip()):
                    raise ValueError("Clue number does not seem correct.")
                # FIXME: this regex needs some fixing... see notebook
                # It splits multi-word answers into the answer and annotation
                # column... it needs to be greedier!
                match = re.search("^\{?\s?[A-Z ]+\s?\}?(\s[-|—|–|–|:]\s)?", line_2)
                answer = line_2[: match.end()].strip(string.whitespace + "-—–:{}")
                annotation = line_2[match.end() :].strip(
                    string.whitespace + string.punctuation + "—"
                )

                clue_number = clue_number.strip(string.whitespace + string.punctuation)
                clue_numbers.append(
                    clue_number
                    + (clue_direction if clue_number[-1] not in ["a", "d"] else "")
                )
                clues.append(clue)
                answers.append(answer)
                annotations.append(annotation)
            except (AttributeError, IndexError, ValueError):
                if line_2 is not None:
                    lines = [line_2] + lines
                else:
                    break

    definitions = extract_definitions(asset_body, clues, 5)

    table = pd.DataFrame([clue_numbers, clues, definitions, answers, annotations]).T
    table.columns = ["clue_number", "clue", "definition", "answer", "annotation"]

    return table
