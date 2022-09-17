from __future__ import annotations

import os
from unittest.mock import PropertyMock

import pytest

from cryptics import config


def test_valid_global_variables():
    assert os.path.exists(config.PROJECT_DIR)
    assert os.path.exists(config.INITIALIZE_DB_SQL)
    assert os.path.exists(config.SQLITE_DATABASE)
    assert set(["User-Agent", "Accept-Encoding"]).issubset(config.HEADERS)


@pytest.mark.parametrize(
    "urls, known_urls, new_urls",
    [
        [list("123"), list("123"), list()],
        [list("123"), list("12"), list("3")],
        [list("123"), list(""), list("123")],
    ],
)
def test_get_new_urls_from_sitemap(
    mocker, urls: list[str], known_urls: list[str], new_urls: list[str]
):
    return_value = "".join([f"<loc>{url}</loc>" for url in urls])
    patched_get = mocker.patch("requests.get")
    type(patched_get.return_value).text = PropertyMock(return_value=return_value)

    # Sanity check on the parametrized arguments
    assert set(known_urls) | set(new_urls) == set(urls)
    assert config.get_new_urls_from_sitemap("sitemap_url", set(known_urls)) == set(
        new_urls
    )


def test_get_new_urls_from_nested_sitemaps(mocker):
    # FIXME: right now this only tests that get_new_urls_from_nested_sitemaps
    # calls get_new_urls_from_sitemap. Ideally we would also test correctness!
    return_value = "".join([f"<loc>sitemap_{i}</loc>" for i in range(3)])
    patched_get = mocker.patch("requests.get")
    type(patched_get.return_value).text = PropertyMock(return_value=return_value)

    patched_get_new_urls = mocker.patch("cryptics.config.get_new_urls_from_sitemap")
    config.get_new_urls_from_nested_sitemaps("", "", set("abc"), config.HEADERS)
    for i in range(3):
        patched_get_new_urls.assert_any_call(f"sitemap_{i}", set("abc"), config.HEADERS)
