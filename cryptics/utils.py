import re
import dateutil


PUZZLE_URL_REGEXES = [
    "^https?://www.theguardian.com/crosswords/.+",
    "^https?://puzzles.independent.co.uk/games/cryptic-crossword-independent/.+",
    "^https?://www.ft.com/content/.+",
    "^https?://www.thetimes.co.uk/puzzles/.+",
    "^https?://puzzles.telegraph.co.uk/.+",
]


def extract_puzzle_name(source_url, soup):
    puzzle_name = None
    if "fifteensquared" in source_url:
        puzzle_name = (
            [s for s in source_url.split("/") if s][-1]
            .title()
            .replace("-", " ")
            .replace("By", "by")
        )
    elif "times-xwd-times" in source_url:
        title = soup.find("title").text
        puzzle_name = re.search("^[A-Za-z ]*[0-9,]+", title).group()
    elif "bigdave44" in source_url:
        title = soup.find("title").text
        puzzle_name = re.search("^[A-Za-z ]*[-—––:\s]*[0-9,]+", title).group()
        if "DT" in puzzle_name:
            puzzle_name = puzzle_name.replace("DT", "Daily Telegraph")
        elif "ST" in puzzle_name:
            puzzle_name = puzzle_name.replace("ST", "Sunday Telegraph")

    return puzzle_name.strip()


def extract_puzzle_date(source_url, soup):
    puzzle_date = None
    if "fifteensquared" in source_url or "bigdave44" in source_url:
        puzzle_date = (
            re.search(r"\d{4}/\d{2}/\d{2}", source_url).group().replace("/", "-")
        )
    elif "times-xwd-times" in source_url:
        entry_date_div = soup.find_all(
            "div", attrs={"class": "asset-meta asset-entry-date"}
        )[0].text.strip()
        puzzle_date = dateutil.parser.parse(entry_date_div).strftime("%Y-%m-%d")

    return puzzle_date.strip()


def extract_puzzle_url(soup):
    try:
        puzzle_urls = [
            link.get("href")
            for link in soup.find_all(
                "a",
                attrs={
                    "href": lambda s: any(
                        [
                            bool(re.findall(puzzle_url_regex, s))
                            for puzzle_url_regex in PUZZLE_URL_REGEXES
                        ]
                    )
                },
            )
        ]
    except:
        return None

    if len(puzzle_urls) == 1:
        return puzzle_urls[0].strip()

    return None


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
    elif table_type == 5:
        raw_definitions = [
            tag.text
            for tag in soup.find_all("u")
            + soup.find_all(
                "span",
                attrs={
                    "style": (lambda s: "underline" in s if s is not None else False)
                },
            )
        ]
    else:
        raise ValueError("`table_type` not recognized.")

    definitions = []
    i = 0

    while raw_definitions:
        definition = raw_definitions.pop(0)
        if definition.strip() in clues[i]:
            if len(definitions) > 0:
                definitions[-1] = "/".join([definitions[-1], definition])
            else:
                definitions.append(definition)
        else:
            # Search for the next clue that contains this definition.
            for j, clue in enumerate(clues[i + 1 :]):
                if definition in clue:
                    if j == 0:
                        definitions.append(definition)
                        i += 1
                    else:
                        definitions.extend(j * ["nan"])
                        raw_definitions = [definition] + raw_definitions
                        i += j
                    break

    if len(definitions) < len(clues):
        while len(definitions) < len(clues):
            definitions.append("nan")
    elif len(definitions) > len(clues):
        raise RuntimeError("More definitions than clues")

    if all(
        [
            all(
                [
                    s.strip().lower() in clue.lower()
                    for s in definition.strip().split("/")
                ]
            )
            or definition == "nan"
            for (definition, clue) in zip(definitions, clues)
        ]
    ):
        return definitions
    else:
        raise RuntimeError("Produced mismatched definitions and clues")
