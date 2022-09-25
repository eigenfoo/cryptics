import re
import string

import bs4
import numpy as np
import pandas as pd

from cryptics.utils import align_suspected_definitions_with_clues, search


def is_parsable_text_type_1(html: str):
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

    Examples:
    - https://times-xwd-times.livejournal.com/2550896.html
    - https://times-xwd-times.livejournal.com/2566520.html
    - https://times-xwd-times.livejournal.com/2566074.html
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


def parse_text_type_1(html: str):
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
    have_clue_number_from_previous_line = False
    clue_direction = None

    while lines:
        line_1 = None
        line_2 = None

        if lines[0].strip(string.whitespace + "\ufeff") == "":
            lines.pop(0)
        elif lines[0].lower() in ["across", "down"]:
            clue_direction = lines.pop(0)
            clue_direction = "a" if "across" in clue_direction.lower() else "d"
        elif lines[0].strip(string.whitespace + "\ufeff").isnumeric():
            # The clue number is its own line, preceding the clue itself. This
            # can happen e.g. when the clue number is a separate column in a
            # table: https://times-xwd-times.livejournal.com/1568749.html
            clue_number = lines.pop(0).strip(string.whitespace + "\ufeff")
            have_clue_number_from_previous_line = True
        else:
            try:
                line_1 = lines.pop(0)
                line_2 = lines.pop(0)

                if have_clue_number_from_previous_line:
                    clue = line_1
                else:
                    clue_number, clue = line_1.split(maxsplit=1)
                have_clue_number_from_previous_line = False

                try:
                    re.search(r"[0-9]+[a|d]?", clue_number.strip())
                except RuntimeError as err:
                    raise RuntimeError("Clue number does not seem correct.") from err
                # FIXME: this regex needs some fixing... see notebook
                # It splits multi-word answers into the answer and annotation
                # column... it needs to be greedier!
                match = search("^\{?\s?[A-Z ]+\s?\}?(\s[-|—|–|–|:]\s)?", line_2)
                answer = line_2[: match.end()].strip(string.whitespace + "-—–:{}")
                annotation = line_2[match.end() :].strip(
                    string.whitespace + string.punctuation + "—"
                )

                clue_number = clue_number.strip(string.whitespace + string.punctuation)
                clue_numbers.append(
                    clue_number
                    + (
                        clue_direction
                        if clue_direction and clue_number[-1] not in ["a", "d"]
                        else ""
                    )
                )
                clues.append(clue)
                answers.append(answer)
                annotations.append(annotation)
            except (AttributeError, IndexError, ValueError):
                if line_2 is not None:
                    lines = [line_2] + lines
                else:
                    break

    definitions = align_suspected_definitions_with_clues(
        clues,
        [
            tag.text
            for tag in soup.find_all("u")
            + soup.find_all(
                "span",
                attrs={
                    "style": (lambda s: "underline" in s if s is not None else False)
                },
            )
        ],
    )

    table = pd.DataFrame([clue_numbers, clues, definitions, answers, annotations]).T
    table.columns = ["clue_number", "clue", "definition", "answer", "annotation"]

    return table


def is_parsable_text_type_2(html: str):
    """
    Identifies if the text looks something like this:

    ACROSS
    1   Emotionally sensitive to mice running all over girl's house (8) EMPATHIC {EM{PAT}{H}IC*}
    6   Network heads of many engineering start-ups harmonise (4) MESH Acrostic
    9   Negligent Milan admits university's past pupils (6) ALUMNI {AL{U}MNI*}

    Examples:

    - https://thehinducrosswordcorner.blogspot.com/2021/07/no-13302-saturday-17-jul-2021-kriskross.html
    - https://thehinducrosswordcorner.blogspot.com/2021/06/no-13278-saturday-19-jun-2021-kriskross.html
    - https://thehinducrosswordcorner.blogspot.com/2021/08/no-13338-saturday-28-aug-2021-arden.html
    """
    soup = bs4.BeautifulSoup(html, "html.parser")
    entry_content = soup.find("div", attrs={"class": lambda s: s in ["entry-content"]})

    # Append a <br> tag after the two ACROSS and DOWN <h4> tags
    for h4 in entry_content.find_all("h4"):
        h4_index = h4.parent.contents.index(h4)
        h4.insert(h4_index + 1, bs4.BeautifulSoup("<br>", features="lxml"))

    # Turn all <br> tags into newlines
    for br in entry_content.find_all("br"):
        br.replace_with("\n")

    return (
        # At least 20 "123a. clue goes here (123)" lines
        20
        <= len(re.findall(r"\s+[0-9]+[a|d]?\.?\s+.*\([0-9, ]+\)", entry_content.text))
        # Around 64 bolded entries (definitions and answers)
        and 64 - 10 <= len(entry_content.find_all("b")) <= 64 + 10
    )


def parse_text_type_2(html: str):
    soup = bs4.BeautifulSoup(html, "html.parser")
    entry_content = soup.find("div", attrs={"class": lambda s: s in ["entry-content"]})

    # Append a <br> tag after the two ACROSS and DOWN <h4> tags
    for h4 in entry_content.find_all("h4"):
        h4_index = h4.parent.contents.index(h4)
        h4.insert(h4_index + 1, bs4.BeautifulSoup("<br>", features="lxml"))

    # Turn all <br> tags into newlines
    for br in entry_content.find_all("br"):
        br.replace_with("\n")

    lines = [line.strip() for line in entry_content.text.splitlines() if line]

    clue_numbers = []
    clues = []
    answers = []
    annotations = []
    clue_direction = "a"

    for line in lines:
        if line.lower() == "down":
            clue_direction = "d"
            continue

        try:
            clue_number_match = search(r"^[0-9]+[a|d]?", line)
        except RuntimeError:
            continue

        try:
            enumeration = search(r"\([0-9,\- ]*\)", line)
            clue = line[clue_number_match.end() : enumeration.end()].strip()
            answer = search(r"^[A-Z\s\-]+\b", line[enumeration.end() :])
            annotation = line[enumeration.end() + answer.end() :].strip()
        except AttributeError:
            # One or more of the fields is missing. This could be due to a line
            # like e.g. "21 See 14 (7)". Just skip it.
            continue

        clue_number = clue_number_match.group()
        if not ("a" in clue_number or "d" in clue_number):
            clue_number += clue_direction

        clue_numbers.append(clue_number)
        clues.append(clue)
        answers.append(answer.group().strip())
        annotations.append(annotation)

    definitions = align_suspected_definitions_with_clues(
        clues, [tag.text for tag in entry_content.find_all("b")]
    )

    return pd.DataFrame(
        data=np.transpose(
            np.array([clue_numbers, answers, clues, annotations, definitions])
        ),
        columns=["clue_number", "answer", "clue", "annotation", "definition"],
    )
