from __future__ import annotations

import json
import logging
from typing import Callable

import pytest

from cryptics.pdfs import pair_strings


@pytest.mark.parametrize(
    "strings, extra_words, expected",
    [
        [["a", "a x"], ["x"], [("a", "a x")]],
        [["a", "a x", "b", "b x"], ["x"], [("a", "a x"), ("b", "b x")]],
        [["a", "b", "b x", "a x"], ["x"], [("a", "a x"), ("b", "b x")]],
    ],
)
def test_pair_strings(strings, extra_words, expected):
    pairs = pair_strings(strings, extra_words)
    assert pairs == set(expected)
