from __future__ import annotations

import json
import logging
from os.path import join
from typing import Callable

import pytest
from bs4 import BeautifulSoup

from cryptics import utils
from cryptics.config import TESTS_DATA_DIR


def test_get_logger():
    logger = utils.get_logger()
    assert isinstance(logger, logging.Logger)


def test_match(mocker):
    pattern = r"abc"
    string = "abcdefghi"

    with pytest.raises(RuntimeError):
        utils.match(r"jkl", string)

    patched_search = mocker.patch("re.match")
    utils.match(pattern, string)
    patched_search.assert_called_once_with(pattern, string)


def test_search(mocker):
    pattern = r"abc"
    string = "abcdefghi"

    with pytest.raises(RuntimeError):
        utils.search(r"jkl", string)

    patched_search = mocker.patch("re.search")
    utils.search(pattern, string)
    patched_search.assert_called_once_with(pattern, string)


def test_filter_strings_by_keyword():
    strings = ["foo bar", "bar baz", "baz qux"]
    assert utils.filter_strings_by_keyword(strings, ["foo"]) == [strings[0]]
    assert utils.filter_strings_by_keyword(strings, ["bar"]) == strings[:2]
    assert utils.filter_strings_by_keyword(strings, ["baz"]) == strings[1:]
    assert utils.filter_strings_by_keyword(strings, ["qux"]) == [strings[-1]]
    assert not utils.filter_strings_by_keyword(strings, ["quux"])


class TestExtractStringFromUrlAndSoup:
    def _assert_extracted(
        self,
        extractors: dict[str, Callable[[str, BeautifulSoup], str]],
        expected_string: str,
    ) -> None:
        source_url = "foobar"
        soup = BeautifulSoup("bazqux", "lxml")
        assert (
            utils.extract_string_from_url_and_soup(source_url, soup, extractors)
            == expected_string
        )

    def test_extract_string_from_url_and_soup(self):
        self._assert_extracted({"foobar": lambda *args: "quux"}, "quux")
        self._assert_extracted({"foo": lambda *args: "quux"}, "quux")
        self._assert_extracted({"foo": lambda _, soup: soup.text}, "bazqux")
        self._assert_extracted({"quux": lambda _, soup: soup.text}, None)

    @pytest.mark.parametrize(
        "source_url_fragment, urls_soups_titles",
        json.load(
            open(join(TESTS_DATA_DIR, "test_extract_puzzle_names.json"), "r")
        ).items(),
    )
    def test_extract_puzzle_name(
        self, source_url_fragment: str, urls_soups_titles: list[list[str | None]]
    ):
        for url, soup, title in urls_soups_titles:
            soup = BeautifulSoup(soup, "lxml") if soup is not None else None
            assert utils.PUZZLE_NAME_EXTRACTORS[source_url_fragment](url, soup) == title

    @pytest.mark.parametrize(
        "source_url_fragment, urls_soups_dates",
        json.load(
            open(join(TESTS_DATA_DIR, "test_extract_puzzle_dates.json"), "r")
        ).items(),
    )
    def test_extract_puzzle_date(self, source_url_fragment, urls_soups_dates):
        for url, soup, date in urls_soups_dates:
            soup = BeautifulSoup(soup, "lxml") if soup is not None else None
            assert utils.PUZZLE_DATE_EXTRACTORS[source_url_fragment](url, soup) == date

    @pytest.mark.parametrize(
        "source_url_fragment, puzzle_urls",
        json.load(
            open(join(TESTS_DATA_DIR, "test_extract_puzzle_urls.json"), "r")
        ).items(),
    )
    def test_extract_puzzle_url(self, source_url_fragment: str, puzzle_urls: list[str]):
        for puzzle_url in puzzle_urls:
            assert (
                utils.PUZZLE_URL_EXTRACTORS[source_url_fragment](
                    None, BeautifulSoup(f'<a href="{puzzle_url}"></a>', "lxml")
                )
                == puzzle_url
            )


@pytest.mark.parametrize(
    "clues, suspected_definitions, expected_definitions",
    json.load(
        open(
            join(TESTS_DATA_DIR, "test_align_suspected_definitions_with_clues.json"),
            "r",
        )
    ),
)
def test_align_suspected_definitions_with_clues(
    clues, suspected_definitions, expected_definitions
):
    assert (
        utils.align_suspected_definitions_with_clues(clues, suspected_definitions)
        == expected_definitions
    )
