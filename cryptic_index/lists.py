import re
from collections import defaultdict
import bs4
import numpy as np
import pandas as pd


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
