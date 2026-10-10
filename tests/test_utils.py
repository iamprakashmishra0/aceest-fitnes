"""Unit tests for the parsing helpers in ``aceest.utils``."""

from aceest.utils import parse_float, parse_int, parse_str


def test_parse_int_valid():
    assert parse_int("42") == 42
    assert parse_int(7.9) == 7


def test_parse_int_invalid_returns_default():
    assert parse_int("abc") is None
    assert parse_int("abc", 5) == 5
    assert parse_int(None, 3) == 3
    assert parse_int("") is None


def test_parse_float_valid():
    assert parse_float("3.5") == 3.5
    assert parse_float(2) == 2.0


def test_parse_float_invalid_returns_default():
    assert parse_float("x") is None
    assert parse_float("", 1.5) == 1.5
    assert parse_float(None) is None


def test_parse_str_trims_and_defaults():
    assert parse_str("  hello  ") == "hello"
    assert parse_str("") == ""
    assert parse_str(None, "fallback") == "fallback"
    assert parse_str("", "fallback") == "fallback"
    assert parse_str(123) == "123"
