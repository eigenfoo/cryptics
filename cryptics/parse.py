import logging

import bs4

from cryptics.lists import (
    is_parsable_list_type_1,
    is_parsable_list_type_2,
    is_parsable_list_type_3,
    is_parsable_list_type_4,
    parse_list_type_1,
    parse_list_type_2,
    parse_list_type_3,
    parse_list_type_4,
)
from cryptics.specials import is_parsable_special_type_1, parse_special_type_1
from cryptics.tables import (
    is_parsable_table_type_1,
    is_parsable_table_type_2,
    is_parsable_table_type_3,
    is_parsable_table_type_4,
    is_parsable_table_type_5,
    parse_table_type_1,
    parse_table_type_2,
    parse_table_type_3,
    parse_table_type_4,
    parse_table_type_5,
)
from cryptics.text import (
    is_parsable_text_type_1,
    is_parsable_text_type_2,
    parse_text_type_1,
    parse_text_type_2,
)
from cryptics.utils import (
    PUZZLE_DATE_EXTRACTORS,
    PUZZLE_NAME_EXTRACTORS,
    PUZZLE_URL_EXTRACTORS,
    extract_string_from_url_and_soup,
    get_logger,
)


def try_to_parse_as(source_url, html, is_parsable_func, parse_func, logger=None):
    if logger is None:
        logger = get_logger()

    try:
        is_parseable = is_parsable_func(html)
    except:
        return None

    if is_parseable:
        logger.info(f"Parsing using {parse_func.__name__}: {source_url}")
        return parse_func(html)


def postprocess_data(data, html, source_url):
    soup = bs4.BeautifulSoup(html, "html.parser")

    data["clue"] = data["clue"].str.strip()
    data["answer"] = data["answer"].str.strip()
    data["definition"] = data["definition"].str.strip()
    data["annotation"] = data["annotation"].str.strip()
    # Instead of removing periods in each parsing function, we can just remove
    # them here - it's simpler.
    data["clue_number"] = data["clue_number"].str.strip().replace(".", "")

    data["puzzle_name"] = extract_string_from_url_and_soup(
        source_url, soup, PUZZLE_NAME_EXTRACTORS
    )
    data["puzzle_date"] = extract_string_from_url_and_soup(
        source_url, soup, PUZZLE_DATE_EXTRACTORS
    )
    data["puzzle_url"] = extract_string_from_url_and_soup(
        source_url, soup, PUZZLE_URL_EXTRACTORS
    )
    data["source_url"] = source_url
    return data


def try_parse(html, source_url):
    data = None

    parsers = [
        (is_parsable_table_type_1, parse_table_type_1),
        (is_parsable_table_type_2, parse_table_type_2),
        (is_parsable_table_type_3, parse_table_type_3),
        (is_parsable_table_type_4, parse_table_type_4),
        (is_parsable_table_type_5, parse_table_type_5),
        (is_parsable_list_type_1, parse_list_type_1),
        (is_parsable_list_type_2, parse_list_type_2),
        (is_parsable_list_type_3, parse_list_type_3),
        (is_parsable_list_type_4, parse_list_type_4),
        (is_parsable_text_type_1, parse_text_type_1),
        (is_parsable_text_type_2, parse_text_type_2),
        (is_parsable_special_type_1, parse_special_type_1),
    ]

    for is_parsable_func, parse_func in parsers:
        data = try_to_parse_as(source_url, html, is_parsable_func, parse_func)
        if data is not None:
            logger.info(f"Successfully parsed: {source_url}")
            return postprocess_data(data, html, source_url)

    return None
