import bs4

from cryptic_info.tables import (
    is_parsable_table_type_1,
    parse_table_type_1,
    is_parsable_table_type_2,
    parse_table_type_2,
)
from cryptic_info.lists import (
    is_parsable_list_type_1,
    parse_list_type_1,
    is_parsable_list_type_2,
    parse_list_type_2,
)
from cryptic_info.utils import extract_puzzle_url


def try_to_parse_as(response, is_parsable_func, parse_func):
    try:
        is_parseable = is_parsable_func(response)
    except:
        return None
        pass

    if is_parseable:
        print(f"Parsing using {parse_func.__name__}")
        return parse_func(response)


def postprocess_data(data, response, source_url):
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    data["PuzzleURL"] = extract_puzzle_url(soup)
    data["SourceURL"] = source_url
    return data


def try_parse(response, source_url):
    data = None

    parsers = [
        (is_parsable_table_type_1, parse_table_type_1),
        (is_parsable_table_type_2, parse_table_type_2),
        (is_parsable_list_type_1, parse_list_type_1),
        (is_parsable_list_type_2, parse_list_type_2),
    ]

    for is_parsable_func, parse_func in parsers:
        data = try_to_parse_as(response, is_parsable_func, parse_func)
        if data is not None:
            return postprocess_data(data, response, source_url)

    return None
