import re
import bs4
import numpy as np
import pandas as pd
from collections import defaultdict

from cryptics.utils import (
    get_across_down_indexes,
    get_smallest_divs,
    extract_definitions,
)


def is_parsable_list_type_1(html):
    """
    Checks that the HTML primarily consists of paragraphs like this:

    <p>
     21
     <span style="color: #3366ff">
      <span style="text-decoration: underline">
       Avoid
      </span>
      newspaper offered around hotel (4)
     </span>
     <br/>
     <strong>
      SHUN
     </strong>
     <br/>
     SUN (newspaper) round H (hotel)
    </p>

    Examples:

    - https://www.fifteensquared.net/2021/05/22/guardian-saturday-puzzle-28446-tramp/
    - https://www.fifteensquared.net/2021/05/23/independent-on-sunday-1630-by-raich/
    - https://www.fifteensquared.net/2021/05/19/guardian-28449-pasquale/
    """
    soup = bs4.BeautifulSoup(html, "html.parser")
    entry_content = soup.find("div", "entry-content")
    paragraphs = entry_content.find_all("p")
    return (
        np.mean(
            [
                set(["span", "strong"]).issubset(
                    set([tag.name for tag in paragraph.find_all()])
                )
                for paragraph in paragraphs
            ]
        )
        >= 0.65
    )


def parse_list_type_1(html):
    soup = bs4.BeautifulSoup(html, "html.parser")
    entry_content = soup.find("div", "entry-content")
    paragraphs = entry_content.find_all("p")

    clue_direction = None
    data = defaultdict(list)

    for paragraph in paragraphs:
        if paragraph.text.strip().lower() == "across":
            clue_direction = "a"
        elif paragraph.text.strip().lower() == "down":
            clue_direction = "d"

        if set(["br", "span", "strong"]).issubset(
            set([tag.name for tag in paragraph.find_all()])
        ):  # TODO: should we make the subset more restrictive? Which tags?
            clue_number = None

            # Break down <br/> tags - they'll just get in the way
            for tag in paragraph.select("br"):
                tag.extract()
            tag_text = [tag.text for tag in paragraph.find_all()]

            # [clue_number (optional), clue, first_definition, ..., last_definition, answer, annotations_in_pieces]
            if re.search(r"^[0-9]+(a|d)?$", tag_text[0].strip()):
                clue_number = tag_text.pop(0)

            clue = tag_text.pop(0)
            (answer_index,) = np.where([text.strip().isupper() for text in tag_text])
            answer_index = answer_index[0]
            answer = tag_text[answer_index]
            definition = "/".join(tag_text[:answer_index])

            if clue_number is None:
                clue_number = paragraph.text[
                    : re.search(re.escape(clue), paragraph.text).start()
                ]

            annotation = paragraph.text[
                re.search(re.escape(answer), paragraph.text).end() :
            ].strip()

            data["clue_number"].append(
                clue_number.strip()
                + (clue_direction if clue_number.strip().isnumeric() else "")
            )
            data["clue"].append(clue)
            data["definition"].append(definition)
            data["answer"].append(answer)
            data["annotation"].append(annotation)
    return pd.DataFrame(data)


def is_parsable_list_type_2(html):
    """
    Checks that the HTML primarily consists of divs like this:

    <div class="fts-subgroup">
      <span class="fts-clue" style="color: #000000">3. </span>
      <em>
        <span class="fts-clue" style="color: #ff0000">Needs a slap when drunk </span>
        <span class="fts-definition" style="color: #800080">walks by the sea</span>
        <span class="fts-clue" style="color: #ff0000"> (10)</span>
      </em>
    </div>

    <div class="fts-subgroup fts-answer">
      <span style="color: #0000ff">ESPLANADES</span>
    </div>

    <div class="fts-subgroup">
      <p><span style="color: #000000">An anagram (”when drunk’) of NEEDS A SLAP</span></p>
    </div>

    Examples:
    - https://www.fifteensquared.net/2021/05/20/independent-10796-by-tees/
    - https://www.fifteensquared.net/2021/05/17/financial-times-16787-by-peto/
    - https://www.fifteensquared.net/2021/06/02/guardian-28461-imogen/
    """
    soup = bs4.BeautifulSoup(html, "html.parser")
    entry_content = soup.find("div", "entry-content")
    smallest_divs = [
        div
        for div in entry_content.find_all("div")
        if not div.find("div") and div.text.strip()
    ]

    return 32 * 3 - 20 <= len(smallest_divs) <= 32 * 3 + 20


def parse_list_type_2(html):
    soup = bs4.BeautifulSoup(html, "html.parser")
    entry_content = soup.find("div", "entry-content")
    smallest_divs = [
        div
        for div in entry_content.find_all("div")
        if not div.find("div") and div.text.strip()
    ]

    (across_index,) = np.where(
        [div.text.strip().lower() == "across" for div in smallest_divs]
    )[0]
    (down_index,) = np.where(
        [div.text.strip().lower() == "down" for div in smallest_divs]
    )[0]

    i = 1
    data = defaultdict(list)

    while i < len(smallest_divs) - 3:
        if any([x in [across_index, down_index] for x in [i, i + 1, i + 2]]):
            i += 1
            continue

        clue_number = None
        clue = None
        definition = None
        answer = None
        annotation = None

        div_1 = smallest_divs[i]
        div_2 = smallest_divs[i + 1]
        div_3 = smallest_divs[i + 2]

        try:
            clue_number = [
                tag.text.strip()
                for tag in div_1.find_all("span")
                if bool(re.match("^[0-9]+$", tag.text.strip(". ")))
            ][0]
            match = re.match(clue_number, div_1.text)
            clue = div_1.text[match.end() :]
            definition = "/".join(
                [
                    tag.text
                    for tag in div_1.find_all("span", attrs={"class": "fts-definition"})
                ]
            )
            answer = div_2.text
            annotation = div_3.text.strip()
            clue_number = clue_number.strip(". ") + (
                "a" if across_index < i < down_index else "d"
            )

            if all([re.match("[0-9]+(a|d)", clue_number), answer.isupper()]):
                data["clue_number"].append(clue_number)
                data["clue"].append(clue)
                data["definition"].append(definition)
                data["answer"].append(answer)
                data["annotation"].append(annotation)
                i += 3
            else:
                i += 1
        except:
            i += 1

    return pd.DataFrame(data)


def is_parsable_list_type_3(html):
    """
    Checks that the HTML primarily consists of paragraphs like this (note that
    this test is fairly crude: it merely counts the number of `p` tags that
    contain `span` tags):

    <p>
      <span style="color: blue">1. <span style="text-decoration: underline">Advantageous</span> to be young with a lisp … (6)<br/></span>
    </p>

    <p>
      <span style="color: #c00000"><strong>USEFUL</strong></span> : …
      <strong><em>pronounced</em></strong>
      (<span style="color: #0000ff">to be …<span style="color: #000000">) </span></span>
      <strong><em><span style="color: blue">with a lisp</span></em></strong>, “youthful”(young).
    </p>

    Examples:

    - https://www.fifteensquared.net/2021/06/01/financial-times-16800-chalmie/
    - https://www.fifteensquared.net/2021/05/21/guardian-cryptic-28451-puck/
    - https://www.fifteensquared.net/2021/05/24/guardian-quiptic-1123-matilda/
    """
    soup = bs4.BeautifulSoup(html, "html.parser")
    entry_content = soup.find("div", "entry-content")
    return (
        32 * 2 - 10
        <= len(
            [
                paragraph
                for paragraph in entry_content.find_all("p")
                if paragraph.find_all("span")
            ]
        )
        <= 32 * 2 + 10
    )


def parse_list_type_3(html):
    soup = bs4.BeautifulSoup(html, "html.parser")
    entry_content = soup.find("div", "entry-content")
    paragraphs = entry_content.find_all("p")

    (across_index,) = np.where(
        [paragraph.text.strip().lower() == "across" for paragraph in paragraphs]
    )[0]
    (down_index,) = np.where(
        [paragraph.text.strip().lower() == "down" for paragraph in paragraphs]
    )[0]

    i = 1
    data = defaultdict(list)

    while i < len(paragraphs) - 3:
        if any([x in [across_index, down_index] for x in [i, i + 1, i + 2]]):
            i += 1
            continue

        clue_number = None
        clue = None
        definition = None
        answer = None
        annotation = None

        p_1 = paragraphs[i]
        p_2 = paragraphs[i + 1]

        try:
            clue_number = re.match(r"^[0-9]+\.?\s*", p_1.text.strip()).group()
            match = re.match(clue_number, p_1.text)
            clue = p_1.text[match.end() :].strip()
            definition = "/".join(
                [
                    tag.text
                    for tag in p_1.find_all(
                        "span", attrs={"style": "text-decoration: underline"}
                    )
                ]
            )
            answer, *annotation = p_2.text.split(":")
            answer = answer.strip()
            annotation = " ".join(annotation)
            clue_number = clue_number.strip(". ") + (
                "a" if across_index < i < down_index else "d"
            )

            if all([re.match("[0-9]+(a|d)", clue_number), answer.isupper()]):
                data["clue_number"].append(clue_number)
                data["clue"].append(clue)
                data["definition"].append(definition)
                data["answer"].append(answer)
                data["annotation"].append(annotation)
                i += 2
            else:
                i += 1
        except:
            i += 1

    return pd.DataFrame(data)


def is_parsable_list_type_4(html):
    """
    Checks that the HTML primarily consists of divs like this:

    <div>
        1   Encourage fight to obtain a <i><b>container </b></i>(3,3)
        <b><span style="color: #2b00fe;">EGG BOX</span></b>
        {EGG}{BOX}
    </div>

    Examples:

    - https://thehinducrosswordcorner.blogspot.com/2021/09/no-13350-monday-13-sep-2021-kriskross.html
    - https://thehinducrosswordcorner.blogspot.com/2021/09/the-sunday-crossword-no-3167-sunday-12.html
    - https://thehinducrosswordcorner.blogspot.com/2021/09/no-13349-friday-10-sep-2021-afterdark.html
    """
    soup = bs4.BeautifulSoup(html, "html.parser")
    entry_content = soup.find("div", attrs={"class": lambda s: s in ["entry-content"]})
    smallest_divs = get_smallest_divs(entry_content)
    out = 32 - 10 <= len(smallest_divs) and 32 - 15 <= sum(
        [bool(div.find_all("i")) for div in smallest_divs]
    )
    return out


def parse_list_type_4(html):
    soup = bs4.BeautifulSoup(html, "html.parser")
    entry_content = soup.find("div", attrs={"class": lambda s: s in ["entry-content"]})
    smallest_divs = get_smallest_divs(entry_content)
    across_index, down_index = get_across_down_indexes(smallest_divs)

    clue_numbers = []
    clues = []
    answers = []
    annotations = []

    for i in range(across_index + 1, len(smallest_divs)):
        if i == down_index:
            continue

        try:
            clue_number = re.search(r"^[0-9]*[a|d]?", smallest_divs[i].text)
            enumeration = re.search(r"\([0-9,\- ]*\)", smallest_divs[i].text)
            clue = smallest_divs[i].text[clue_number.end() : enumeration.end()].strip()
            answer = re.search(
                r"^[A-Z\s\-]+\b", smallest_divs[i].text[enumeration.end() :]
            )
            annotation = (
                smallest_divs[i].text[enumeration.end() + answer.end() :].strip()
            )
        except AttributeError:
            continue

        clue_number = clue_number.group()
        if not ("a" in clue_number or "d" in clue_number):
            clue_number += "a" if across_index < i and i < down_index else "d"

        clue_numbers.append(clue_number)
        clues.append(clue)
        answers.append(answer.group().strip())
        annotations.append(annotation)

    definitions = extract_definitions(
        entry_content, clues, [tag.text for tag in entry_content.find_all("i")]
    )

    out = pd.DataFrame(
        data=np.transpose(np.array([clue_numbers, answers, clues, annotations])),
        columns=["clue_number", "answer", "clue", "annotation"],
    )
    if definitions is not None:
        out["definition"] = definitions

    return out
