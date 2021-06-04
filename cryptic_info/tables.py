import re

import bs4
import numpy as np
import pandas as pd


def is_parsable_table_type_1(response):
    tables = pd.read_html(response.text)
    for table in tables:
        try:
            if _is_parsable_table_type_1(table):
                return True
        except:
            pass
    return False


def _is_parsable_table_type_1(table):
    """
    Identifies if a table looks like this:

            0          1                                                                    2
    0  ACROSS     ACROSS                                                               ACROSS
    1       1   ORGANIST                              Key worker possibly having to pedal (8)
    2     NaN        NaN                                                   Cryptic definition
    3       6     MEASLY                 Paltry bite to eat finally snaffled with cunning (6)
    4     NaN        NaN        MEA(l) ("bite to eat", finally snaffled) with SLY ("cunning")
                                             ...
    33   DOWN       DOWN                                                                 DOWN
    34      2  REPROBATE                              Record loot hoarded by rank villain (9)
    35    NaN        NaN  EP (extended play "record") + ROB ("loot") hoarded by RATE ("rank")
    36      3      ADIOS                       Spanish Cheers run dropped from broadcasts (5)
    37    NaN        NaN             R (run, in cricket) dropped from (r)ADIOS ("broadcasts")
                                             ...
    """
    return all(
        [
            # There is a row that says ACROSS in all cells
            (table.astype(str).applymap(str.lower) == "across").all(axis=1).any(),
            # There is a row that says DOWN in all cells
            (table.astype(str).applymap(str.lower) == "down").all(axis=1).any(),
            # Asides from the ACROSS and DOWN rows, the first two colums are exactly half NaN
            2 * table[[0, 1]].isna().all(axis=1).sum() == table.shape[0] - 2,
            # The first column (except for the ACROSS and DOWN rows) is all numeric
            # This is what we expect to be the clue numbers
            # FIXME: double entry?
            all(
                [
                    s.lower() in ["across", "down"] or any([c.isdigit() for c in s])
                    for s in table[0].dropna()
                ]
            ),
            # The second column (except for the ACROSS and DOWN rows) is all uppercase
            # This is what we expect to be the answers
            all(
                [
                    s.lower() in ["across", "down"] or s.isupper()
                    for s in table[1].dropna()
                ]
            ),
            # The third column (except for the ACROSS and DOWN rows) has around half of its
            # rows ending in enumerations, give or take 4
            # FIXME: some enumerations can be (10, hyph.) or (12, two wds.)
            np.abs(
                (
                    sum(
                        [
                            s.lower() in ["across", "down"]
                            or bool(re.findall("\([0-9,\- ]+\)$", s))
                            for s in table[2].dropna()
                        ]
                    )
                    - 2
                )
                - ((table.shape[0] - 2) / 2)
            )
            <= 4,
        ]
    )


def parse_table_type_1(response):
    tables = pd.read_html(response.text)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    for table in tables:
        if _is_parsable_table_type_1(table):
            return _parse_table_type_1(table, soup)


def _parse_table_type_1(table, soup):
    (across_index,) = np.where(table[0].str.lower() == "across")[0]
    (down_index,) = np.where(table[0].str.lower() == "down")[0]

    # Clue numbers
    raw_clue_numbers = table[0].astype(str)

    clue_numbers = []
    for i, row in enumerate(raw_clue_numbers):
        if i == across_index or i == down_index:
            continue
        elif row != "nan" and across_index < i < down_index:
            clue_numbers.append(row + "a")
        elif row != "nan":
            clue_numbers.append(row + "d")

    # Answers
    raw_answers = table[1].str.upper().drop([across_index, down_index])
    answers = raw_answers[::2].tolist()

    # Clues and annotations
    clues_and_annotations = table[2].drop([across_index, down_index])
    clues = clues_and_annotations[::2].tolist()
    annotations = clues_and_annotations[1::2].tolist()
    definitions = extract_definitions(soup, clues, table_type=1)

    out = pd.DataFrame(
        data=np.transpose(np.array([clue_numbers, answers, clues, annotations])),
        columns=["ClueNumber", "Answer", "Clue", "Annotation"],
    )
    if definitions is not None:
        out["Definition"] = definitions

    return out


def is_parsable_table_type_2(response):
    tables = pd.read_html(response.text)
    for table in tables:
        try:
            if _is_parsable_table_type_2(table):
                return True
        except:
            pass
    return False


def _is_parsable_table_type_2(table):
    """
    Identifies if a table looks like this (possibly with extra columns filled
    with NaNs):

            0         1                                                 2
    0  Across    Across                                            Across
    1       8  TWENTIES  They roared ... (8)Reference to the “Roaring ...
                                             ...
    15   Down      Down                                              Down
    16     2       UNDO   Found out concealing ... (4)Hidden in foUND Out
    """
    return all(
        [
            # There is a row that says ACROSS in all cells
            (table.astype(str).applymap(str.lower) == "across").all(axis=1).any(),
            # There is a row that says DOWN in all cells
            (table.astype(str).applymap(str.lower) == "down").all(axis=1).any(),
            # The first column (except for the ACROSS and DOWN rows) is all numeric
            # This is what we expect to be the clue numbers
            # FIXME: double entry?
            all(
                [
                    s.lower() in ["across", "down"] or any([c.isdigit() for c in s])
                    for s in table[0]
                ]
            ),
            # The second column (except for the ACROSS and DOWN rows) is all uppercase
            # This is what we expect to be the answers
            all([s.lower() in ["across", "down"] or s.isupper() for s in table[1]]),
            # The third column (except for the ACROSS and DOWN rows) has contains an
            # enumeration, which is flanked by clue and annotation
            all(
                [
                    s.lower() in ["across", "down"]
                    or bool(re.findall(".+\([0-9,\- ]+\).+", s))
                    for s in table[2]
                ]
            ),
        ]
    )


def parse_table_type_2(response):
    tables = pd.read_html(response.text)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    for table in tables:
        if _is_parsable_table_type_2(table):
            return _parse_table_type_2(table, soup)


def _parse_table_type_2(table, soup):
    # Cut out any extraneous columns
    table = table.iloc[:, :3]

    table = table.rename(columns={0: "ClueNumber", 1: "Answer", 2: "ClueAndAnnotation"})

    # Append "a" to across clue numbers, and "d" to down clue numbers
    (across_index,) = np.where(table["ClueNumber"].str.lower() == "across")[0]
    (down_index,) = np.where(table["ClueNumber"].str.lower() == "down")[0]
    table.iloc[across_index + 1 : down_index]["ClueNumber"] += "a"
    table.iloc[down_index + 1 :]["ClueNumber"] += "d"

    # Drop rows that are entirely "Across" and "Down"
    table = table.drop([across_index, down_index]).reset_index(drop=True)

    # Separate clue and annotation
    clues_and_annotations = pd.DataFrame(
        table["ClueAndAnnotation"].apply(separate_clue_and_annotation).tolist()
    ).rename(columns={0: "Clue", 1: "Annotation"})

    table = pd.concat([table, clues_and_annotations], axis=1)
    table = table.drop(columns=["ClueAndAnnotation"])

    # Add definitions
    definitions = extract_definitions(soup, table["Clue"], table_type=2)
    if definitions is not None:
        table["Definition"] = definitions

    return table


def separate_clue_and_annotation(s):
    match = re.search("\([0-9,\- ]+\)", s)
    if match is None:
        print(s)
    clue = s[: match.end()].strip()
    annotation = s[match.end() :].strip()
    return clue, annotation


def extract_definitions(soup, clues, table_type):
    if table_type == 1:
        raw_definitions = [
            tag.text
            for tag in soup.find_all(
                "span",
                attrs={"style": (lambda s: ("underline" in s or "u" in s) if s is not None else False)},
            )
        ]
    elif table_type == 2:
        raw_definitions = [tag.text for tag in soup.find_all("u")]

    definitions = []
    i = 0

    while raw_definitions:
        definition = raw_definitions.pop(0)
        if definition in clues[i]:
            if len(definitions) > 0:
                definitions[-1] = "/".join([definitions[-1], definition])
            else:
                definitions.append(definition)
        elif definition in clues[i + 1]:
            definitions.append(definition)
            i += 1
        elif definition in clues[i + 2]:
            definitions.append("nan")
            raw_definitions = [definition] + raw_definitions
            i += 1

    if len(definitions) < len(clues):
        while len(definitions) < len(clues):
            definitions.append("nan")
    elif len(definitions) > len(clues):
        return None

    if all(
        [
            all([s.lower() in clue.lower() for s in definition.split("/")])
            or definition == "nan"
            for (definition, clue) in zip(definitions, clues)
        ]
    ):
        return definitions
    else:
        return None
