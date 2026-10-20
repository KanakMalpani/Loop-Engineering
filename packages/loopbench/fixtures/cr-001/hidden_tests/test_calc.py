import pytest
from calc import parse_int
def test_ok(): assert parse_int(" 42 ") == 42
def test_neg(): assert parse_int("-7") == -7
def test_bad_raises():
    with pytest.raises(ValueError): parse_int("abc")
def test_none_raises():
    with pytest.raises(ValueError): parse_int(None)
