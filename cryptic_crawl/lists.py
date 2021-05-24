import re
from collections import defaultdict
import numpy as np
import pandas as pd


def is_parsable_list(paragraphs):
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


def parse_list(paragraphs):
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
            ]

            data["ClueNumber"].append(
                clue_number.strip()
                + (clue_direction if clue_number.strip().isnumeric() else "")
            )
            data["Clue"].append(clue)
            data["Definition"].append(definition)
            data["Answer"].append(answer)
            data["Annotation"].append(annotation)
    return pd.DataFrame(data)
