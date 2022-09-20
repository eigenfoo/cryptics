from __future__ import annotations

import itertools
import os
from unittest.mock import PropertyMock

import pytest

from cryptics import config


def test_valid_global_variables():
    assert os.path.exists(config.PROJECT_DIR)
    assert os.path.exists(config.INITIALIZE_DB_SQL)
    # This only exists on my local machine.
    # assert os.path.exists(config.SQLITE_DATABASE)
    assert set(["User-Agent", "Accept-Encoding"]).issubset(config.HEADERS)


@pytest.mark.parametrize(
    "urls, known_urls, expected_new_urls",
    [
        [list("123"), list("123"), list()],
        [list("123"), list("12"), list("3")],
        [list("123"), list(""), list("123")],
    ],
)
def test_get_new_urls_from_sitemap(
    mocker, urls: list[str], known_urls: list[str], expected_new_urls: list[str]
):
    # Mock the result of requests.get with an object that has a .text property.
    return_value = "".join([f"<loc>{url}</loc>" for url in urls])
    patched_get = mocker.patch("requests.get")
    type(patched_get.return_value).text = PropertyMock(return_value=return_value)

    # Sanity check on the parametrized arguments.
    assert set(known_urls) | set(expected_new_urls) == set(urls)
    assert config.get_new_urls_from_sitemap("sitemap_url", set(known_urls)) == set(
        expected_new_urls
    )


@pytest.mark.parametrize(
    "nested_new_urls, expected_new_urls",
    [
        [[], []],
        [[["1"], ["2"]], list("12")],
        [[["1"], ["2"], ["3"]], list("123")],
    ],
)
def test_get_new_urls_from_nested_sitemaps(
    mocker, nested_new_urls: list[list[str]], expected_new_urls: list[str]
):
    """Tests that get_new_urls_from_nested_sitemaps returns the union of return
    values from get_url_from_sitemap. Note that this does does _not_ test for
    correct behavior of `known_urls`, as that behavior is tested in
    test_get_new_urls_from_sitemap.

    nested_new_urls: list of lists of "URLs", which will be mocked to be the
        return values of successive calls to get_new_urls_from_sitemap.
    expected_new_urls: list of URLs that should be returned by
        get_new_urls_from_nested_sitemaps.
    """
    # Mock the result of requests.get with an object that has a .text property.
    nested_sitemaps = "".join(
        [f"<loc>sitemap_{i}</loc>" for i in range(len(nested_new_urls))]
    )
    patched_get = mocker.patch("requests.get")
    type(patched_get.return_value).text = PropertyMock(return_value=nested_sitemaps)

    # Additionally, patch cryptics.config.get_new_urls_from_sitemap
    patched_get_new_urls = mocker.patch("cryptics.config.get_new_urls_from_sitemap")
    patched_get_new_urls.side_effect = nested_new_urls

    new_urls = config.get_new_urls_from_nested_sitemaps(
        sitemap_url="sitemap_url",
        nested_sitemap_regex=r"sitemap_",
        # Correct behavior of known_urls is tested in
        # test_get_new_urls_from_sitemap.
        known_urls=set(),
        headers=config.HEADERS,
    )

    # The implementation of get_new_urls_from_nested_sitemaps should call
    # get_new_urls_from_sitemap.
    for i in range(len(nested_new_urls)):
        patched_get_new_urls.assert_any_call(f"sitemap_{i}", set(), config.HEADERS)

    # Sanity check on the parametrized arguments.
    assert list(itertools.chain(*nested_new_urls)) == expected_new_urls

    assert new_urls == set(expected_new_urls)
