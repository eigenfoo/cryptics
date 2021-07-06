import re

import bs4
import numpy as np
import pandas as pd


def is_parsable_table_type_1(html):
    tables = pd.read_html(html)
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
            np.abs(
                (
                    sum(
                        [
                            s.lower() in ["across", "down"]
                            or bool(re.findall("\([0-9,\- ]+(?:[\w\.]+)?\)$", s))
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


def parse_table_type_1(html):
    tables = pd.read_html(html)
    soup = bs4.BeautifulSoup(html, "html.parser")
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
        columns=["clue_number", "answer", "clue", "annotation"],
    )
    if definitions is not None:
        out["definition"] = definitions

    return out


def is_parsable_table_type_2(html):
    tables = pd.read_html(html)
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
            # The third column (except for the ACROSS and DOWN rows) contains
            # an enumeration, which is flanked by clue and annotation
            all(
                [
                    s.lower() in ["across", "down"]
                    or bool(re.findall(".+\([0-9,\- ]+(?:[\w\.]+)?\).+", s))
                    for s in table[2]
                ]
            ),
        ]
    )


def parse_table_type_2(html):
    tables = pd.read_html(html)
    soup = bs4.BeautifulSoup(html, "html.parser")
    for table in tables:
        if _is_parsable_table_type_2(table):
            return _parse_table_type_2(table, soup)


def _parse_table_type_2(table, soup):
    # Cut out any extraneous columns
    table = table.iloc[:, :3]

    table = table.rename(
        columns={0: "clue_number", 1: "answer", 2: "ClueAndAnnotation"}
    )

    # Append "a" to across clue numbers, and "d" to down clue numbers
    (across_index,) = np.where(table["clue_number"].str.lower() == "across")[0]
    (down_index,) = np.where(table["clue_number"].str.lower() == "down")[0]
    table.iloc[across_index + 1 : down_index]["clue_number"] += "a"
    table.iloc[down_index + 1 :]["clue_number"] += "d"

    # Drop rows that are entirely "Across" and "Down"
    table = table.drop([across_index, down_index]).reset_index(drop=True)

    def separate_clue_and_annotation(s):
        match = re.search("\([0-9,\- ]+(?:[\w\.]+)?\)", s)
        if match is None:
            print(s)
        clue = s[: match.end()].strip()
        annotation = s[match.end() :].strip()
        return clue, annotation

    # Separate clue and annotation
    clues_and_annotations = pd.DataFrame(
        table["ClueAndAnnotation"].apply(separate_clue_and_annotation).tolist()
    ).rename(columns={0: "clue", 1: "annotation"})

    table = pd.concat([table, clues_and_annotations], axis=1)
    table = table.drop(columns=["ClueAndAnnotation"])

    # Add definitions
    definitions = extract_definitions(soup, table["clue"], table_type=2)
    if definitions is not None:
        table["definition"] = definitions

    return table


def extract_definitions(soup, clues, table_type):
    if table_type == 1:
        raw_definitions = [
            tag.text
            for tag in soup.find_all(
                "span",
                attrs={
                    "style": (lambda s: "underline" in s if s is not None else False)
                },
            )
            + soup.find_all(
                "span",
                attrs={
                    "class": (
                        lambda s: "fts-definition" in s if s is not None else False
                    )
                },
            )
        ]
    elif table_type == 2 or table_type == 4:
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


def is_parsable_table_type_3(html):
    tables = pd.read_html(html)
    for table in tables:
        try:
            if _is_parsable_table_type_3(table):
                return True
        except:
            pass
    return False


def _is_parsable_table_type_3(table):
    """
    Identifies if a table looks like this:

         Across  Across.1              Across.2    Across.3  Across.4
     0  Clue No  Solution                  Clue  Definition       NaN
     1       1A    SUBWAY  Undermining Boris...    S(UBW)AY       NaN
                                    ...
    17     Down      Down                  Down        Down      Down
    18  Clue No  Solution                  Clue  Definition       NaN
    19       1D    SAMPLE      Sperm donor’s...   S + AMPLE       NaN
    """
    return all(
        [
            # The index looks like ['Across', 'Across.1', 'Across.2', ...]
            all(["across" in column.lower() for column in table.columns]),
            # There is a row that says 'Down' in all cells
            (table.astype(str).applymap(str.lower) == "down").all(axis=1).any(),
            # The first column (except for the 'Across', 'Down' and 'Clue No' rows)
            # is all numeric. This is what we expect to be the clue numbers
            all(
                [
                    s.lower() in ["across", "down", "clue no"]
                    or any([c.isdigit() for c in s])
                    for s in table.iloc[:, 0].dropna()
                ]
            ),
            # The second column (except for the 'Across', 'Down' and 'Solution' rows)
            # is all uppercase. This is what we expect to be the answers
            all(
                [
                    s.lower() in ["across", "down", "solution"] or s.isupper()
                    for s in table.iloc[:, 1].dropna()
                ]
            ),
            # The third column (except for the 'Across', 'Down' and 'Clue' rows) all end
            # in enumerations, give or take 5. This is what we expect to be the clues
            np.abs(
                sum(
                    [
                        s.lower() in ["across", "down", "clue"]
                        or bool(re.findall("\([0-9,\- ]+(?:[\w\.]+)?\)$", s))
                        for s in table.iloc[:, 2].dropna()
                    ]
                )
                - table.shape[0]
            )
            <= 5,
        ]
    )


def parse_table_type_3(html):
    tables = pd.read_html(html)
    for table in tables:
        if _is_parsable_table_type_3(table):
            return _parse_table_type_3(table)


def _parse_table_type_3(table):
    # The column names are ['Across', 'Across.1', 'Across.2', ...]
    # Make them just another row, for simplicity
    table = table.T.reset_index().T.reset_index(drop=True)

    # Drop the first (i.e. the 'Across') row and the 'Down' row,
    # and the rows that follow them, which are the column names
    (down_index,) = np.where(table[0].str.lower() == "down")[0]
    table = table.drop([0, 1, down_index, down_index + 1])

    table = table.iloc[:, :4]  # Drop extraneous columns

    table.columns = ["clue_number", "answer", "clue", "DefinitionAndAnnotation"]
    table["clue_number"] = table["clue_number"].str.lower()
    table["definition"] = table["DefinitionAndAnnotation"].apply(
        lambda s: "/".join(s.split(" / ")[:-1])
    )
    table["annotation"] = table["DefinitionAndAnnotation"].apply(
        lambda s: s.split(" / ")[-1]
    )
    table = table.drop(columns=["DefinitionAndAnnotation"])
    return table


def is_parsable_table_type_4(html):
    tables = pd.read_html(html)
    for table in tables:
        try:
            if _is_parsable_table_type_4(table):
                return True
        except:
            pass
    return False


def _is_parsable_table_type_4(table):
    return all(
        [
            # The first row is ["No", "Clue", "Wordplay", "Entry"]
            all(["No", "clue", "Wordplay", "Entry"] == table.iloc[0]),
            # The first column contains 'Across' and 'Down'
            all([any(x == table[0].str.lower()) for x in ["across", "down"]]),
            # The first column (except for the 'Across', 'Down' and 'No' rows)
            # is all numeric. This is what we expect to be the clue numbers
            all(
                [
                    s.lower() in ["across", "down", "no"]
                    or any([c.isdigit() for c in s])
                    for s in table.iloc[:, 0].dropna()
                ]
            ),
            # The second column (except for the 'Across', 'Down' and 'Clue' rows) all end
            # in enumerations, give or take 5. This is what we expect to be the clues
            np.abs(
                sum(
                    [
                        s.lower() in ["across", "down", "clue"]
                        or bool(re.findall("\([0-9,\- ]+(?:[\w\.]+)?\)$", s))
                        for s in table.iloc[:, 1].dropna()
                    ]
                )
                - table.shape[0]
            )
            <= 5,
        ]
    )


def parse_table_type_4(html):
    tables = pd.read_html(html)
    soup = bs4.BeautifulSoup(html, "lxml")
    for table in tables:
        if _is_parsable_table_type_4(table):
            return _parse_table_type_4(table, soup)


def _parse_table_type_4(table, soup):
    """
    Identifies if a table looks like this:

            0            1               2            3
    0      No         Clue        Wordplay        Entry
    1  Across          NaN             NaN          NaN
    2       1   Frantic...   Anagram of...  LAST MINUTE
                            ...
    16   Down          NaN             NaN          NaN
    17 	    1   Delayed...   Anagram of...         LATE
    """
    # Append clue directions to clue numbers
    (down_index,) = np.where(table[0].str.lower() == "down")[0]
    table.iloc[2:down_index, 0] += "a"
    table.iloc[down_index + 1 :, 0] += "d"

    # Drop the first row and the 'Across' and 'Down' rows
    table = table.drop([0, 1, down_index]).reset_index(drop=True)
    table = table.iloc[:, :4]  # Drop extraneous columns
    table.columns = ["clue_number", "clue", "annotation", "answer_with_explanation"]

    def separate_definition_and_explanation(s):
        match = re.search("^[A-Z'\- ]+", s.strip())
        definition = s[: match.end()].strip()
        explanation = s[match.end() :].strip()
        return definition, explanation

    definitions_and_explanations = pd.DataFrame(
        table["answer_with_explanation"]
        .apply(separate_definition_and_explanation)
        .tolist(),
        columns=["answer", "explanation"],
    )

    # Append the explanation of the answer to the annotation
    table = pd.concat([table, definitions_and_explanations], axis=1)
    table["annotation"] = table["annotation"] + " " + table["explanation"]
    table = table.drop(columns=["answer_with_explanation", "explanation"])

    definitions = extract_definitions(soup, table["clue"], table_type=4)
    if definitions is not None:
        table["definition"] = definitions

    return table
