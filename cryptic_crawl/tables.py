import re
import numpy as np
import pandas as pd


def is_parsable_table(table):
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
                    s in ["ACROSS", "DOWN"] or any([c.isdigit() for c in s])
                    for s in table[0].dropna()
                ]
            ),
            # The second column (except for the ACROSS and DOWN rows) is all uppercase
            # This is what we expect to be the answers
            all([s in ["ACROSS", "DOWN"] or s.isupper() for s in table[1].dropna()]),
            # The third column (except for the ACROSS and DOWN rows) has around half of its
            # rows ending in enumerations, give or take 4
            # FIXME: some enumerations can be (10, hyph.) or (12, two wds.)
            np.abs(
                (
                    sum(
                        [
                            s in ["ACROSS", "DOWN"]
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


def parse_table(table, soup):
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
    definitions = extract_definitions(soup, clues)

    out = pd.DataFrame(
        data=np.transpose(np.array([clue_numbers, answers, clues, annotations])),
        columns=["ClueNumber", "Answer", "Clue", "Annotation"],
    )
    if definitions is not None:
        out["Definition"] = definitions

    return out


def extract_definitions(soup, clues):
    raw_definitions = [
        tag.text
        for tag in soup.find_all(
            "span",
            attrs={"style": (lambda s: "underline" in s if s is not None else False)},
        )
    ]

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
