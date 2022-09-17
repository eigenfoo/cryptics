from __future__ import annotations

import json
import logging
from typing import Callable

import pytest
from bs4 import BeautifulSoup

from cryptics import utils


def test_get_logger():
    logger = utils.get_logger()
    assert isinstance(logger, logging.Logger)


def test_search():
    assert utils.search(r"def", "def") == "def"
    assert utils.search(r"def", "abcdefghi") == "def"
    assert utils.search(r"def", "abcdefghidefghi") == "def"
    assert utils.search(r"def(.{3})", "abcdefghi") == "defghi"
    assert utils.search(r"def(.{3})", "abcdefghi", group=1) == "ghi"
    with pytest.raises(IndexError):
        utils.search(r"def", "abcdefghi", group=1)
    with pytest.raises(RuntimeError):
        utils.search(r"jkl", "abcdefghi")


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
        json.load(open("tests/test_extract_puzzle_names.json", "r")).items(),
    )
    def test_extract_puzzle_name(
        self, source_url_fragment: str, urls_soups_titles: list[list[str | None]]
    ):
        for url, soup, title in urls_soups_titles:
            soup = BeautifulSoup(soup, "lxml") if soup is not None else None
            assert utils.PUZZLE_NAME_EXTRACTORS[source_url_fragment](url, soup) == title

    @pytest.mark.parametrize(
        "source_url_fragment, urls_soups_dates",
        json.load(open("tests/test_extract_puzzle_dates.json", "r")).items(),
    )
    def test_extract_puzzle_date(self, source_url_fragment, urls_soups_dates):
        for url, soup, date in urls_soups_dates:
            soup = BeautifulSoup(soup, "lxml") if soup is not None else None
            assert utils.PUZZLE_DATE_EXTRACTORS[source_url_fragment](url, soup) == date

    @pytest.mark.parametrize(
        "source_url_fragment, puzzle_urls",
        json.load(open("tests/test_extract_puzzle_urls.json", "r")).items(),
    )
    def test_extract_puzzle_url(self, source_url_fragment: str, puzzle_urls: list[str]):
        for puzzle_url in puzzle_urls:
            assert (
                utils.PUZZLE_URL_EXTRACTORS[source_url_fragment](
                    None, BeautifulSoup(f'<a href="{puzzle_url}"></a>', "lxml")
                )
                == puzzle_url
            )
