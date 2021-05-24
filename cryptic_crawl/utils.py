import re

PUZZLE_URL_REGEXES = [
    "^https?://www.theguardian.com/crosswords/.+",
    "^https?://puzzles.independent.co.uk/games/cryptic-crossword-independent/.+",
    "^https?://www.ft.com/content/.+",
    "^https?://www.thetimes.co.uk/puzzles/.+",
]


def extract_puzzle_url(soup):
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

    if len(puzzle_urls) == 1:
        return puzzle_urls[0]

    return None
