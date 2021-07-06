import re
import dateutil


PUZZLE_URL_REGEXES = [
    "^https?://www.theguardian.com/crosswords/.+",
    "^https?://puzzles.independent.co.uk/games/cryptic-crossword-independent/.+",
    "^https?://www.ft.com/content/.+",
    "^https?://www.thetimes.co.uk/puzzles/.+",
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
        puzzle_name = re.search("^[A-Za-z ]*[0-9]+", title).group()

    return puzzle_name


def extract_puzzle_date(source_url, soup):
    puzzle_date = None
    if "fifteensquared" in source_url:
        puzzle_date = (
            re.search(r"\d{4}/\d{2}/\d{2}", source_url).group().replace("/", "-")
        )
    elif "times-xwd-times" in source_url:
        entry_date_div = soup.find_all(
            "div", attrs={"class": "asset-meta asset-entry-date"}
        )[0].text.strip()
        puzzle_date = dateutil.parser.parse(entry_date_div).strftime("%Y-%m-%d")

    return puzzle_date


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
        return puzzle_urls[0]

    return None
