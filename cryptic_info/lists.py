import re
from collections import defaultdict
import bs4
import numpy as np
import pandas as pd


def is_parsable_list_type_1(response):
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
    soup = bs4.BeautifulSoup(response.text, "html.parser")
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


def parse_list_type_1(response):
    soup = bs4.BeautifulSoup(response.text, "html.parser")
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

            data["ClueNumber"].append(
                clue_number.strip()
                + (clue_direction if clue_number.strip().isnumeric() else "")
            )
            data["Clue"].append(clue)
            data["Definition"].append(definition)
            data["Answer"].append(answer)
            data["Annotation"].append(annotation)
    return pd.DataFrame(data)


def is_parsable_list_type_2(response):
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    entry_content = soup.find("div", "entry-content")
    smallest_divs = [
        div
        for div in entry_content.find_all("div")
        if not div.find("div") and div.text.strip()
    ]

    return 32 * 3 - 10 <= len(smallest_divs) <= 32 * 3 + 10


def parse_list_type_2(response):
    soup = bs4.BeautifulSoup(response.text, "html.parser")
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
                data["ClueNumber"].append(clue_number)
                data["Clue"].append(clue)
                data["Definition"].append(definition)
                data["Answer"].append(answer)
                data["Annotation"].append(annotation)
                i += 3
            else:
                i += 1
        except:
            i += 1

    return pd.DataFrame(data)
