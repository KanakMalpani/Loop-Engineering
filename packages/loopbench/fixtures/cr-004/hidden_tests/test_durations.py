import pytest
from durations import parse_duration


def test_hours_only():
    assert parse_duration("2h") == 7200


def test_hours_with_minutes():
    assert parse_duration("1h30m") == 5400


def test_zero_hours_with_minutes():
    assert parse_duration("0h45m") == 2700


def test_minutes_only():
    assert parse_duration("45m") == 2700


def test_seconds_only():
    assert parse_duration("45s") == 45


def test_all_three_units():
    assert parse_duration("1h2m3s") == 3723


def test_uppercase_units():
    assert parse_duration("1H30M") == 5400


def test_surrounding_whitespace():
    assert parse_duration("  1h30m\n") == 5400


def test_invalid_text_rejected():
    with pytest.raises(ValueError):
        parse_duration("abc")


def test_empty_text_rejected():
    with pytest.raises(ValueError):
        parse_duration("")
    with pytest.raises(ValueError):
        parse_duration("   ")


def test_repeated_unit_rejected():
    with pytest.raises(ValueError):
        parse_duration("1h2h")


def test_non_string_rejected():
    with pytest.raises(ValueError):
        parse_duration(None)
