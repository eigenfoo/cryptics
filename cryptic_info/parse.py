import bs4

from cryptic_info.text import (
    is_parsable_text_type_1,
    parse_text_type_1,
)
from cryptic_info.tables import (
    is_parsable_table_type_1,
    parse_table_type_1,
    is_parsable_table_type_2,
    parse_table_type_2,
    is_parsable_table_type_3,
    parse_table_type_3,
    is_parsable_table_type_4,
    parse_table_type_4,
)
from cryptic_info.lists import (
    is_parsable_list_type_1,
    parse_list_type_1,
    is_parsable_list_type_2,
    parse_list_type_2,
    is_parsable_list_type_3,
    parse_list_type_3,
)
from cryptic_info.utils import extract_puzzle_name, extract_puzzle_date, extract_puzzle_url


def try_to_parse_as(html, is_parsable_func, parse_func):
    try:
        is_parseable = is_parsable_func(html)
    except:
        return None
        pass

    if is_parseable:
        print(f"Parsing using {parse_func.__name__}")
        return parse_func(html)


def postprocess_data(data, html, source_url):
    soup = bs4.BeautifulSoup(html, "html.parser")
    data["puzzle_name"] = extract_puzzle_name(source_url, soup)
    data["puzzle_date"] = extract_puzzle_date(source_url, soup)
    data["puzzle_url"] = extract_puzzle_url(soup)
    data["source_url"] = source_url
    return data


def try_parse(html, source_url):
    data = None

    parsers = [
        (is_parsable_table_type_1, parse_table_type_1),
        (is_parsable_table_type_2, parse_table_type_2),
        (is_parsable_table_type_3, parse_table_type_3),
        (is_parsable_table_type_4, parse_table_type_4),
        (is_parsable_list_type_1, parse_list_type_1),
        (is_parsable_list_type_2, parse_list_type_2),
        (is_parsable_list_type_3, parse_list_type_3),
        (is_parsable_text_type_1, parse_text_type_1),
    ]

    for is_parsable_func, parse_func in parsers:
        data = try_to_parse_as(html, is_parsable_func, parse_func)
        if data is not None:
            return postprocess_data(data, html, source_url)

    return None
