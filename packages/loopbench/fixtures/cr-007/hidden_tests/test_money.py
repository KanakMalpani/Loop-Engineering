import pytest
from money import split_cents


def test_even_split_when_no_remainder():
    assert split_cents(10, 2) == [5, 5]


def test_parts_sum_to_total():
    assert sum(split_cents(10, 3)) == 10
    assert len(split_cents(10, 3)) == 3


def test_remainder_is_front_loaded():
    assert split_cents(10, 3) == [4, 3, 3]


def test_wider_remainder_is_front_loaded():
    assert split_cents(10, 4) == [3, 3, 2, 2]


def test_single_part_is_the_total():
    assert split_cents(7, 1) == [7]


def test_zero_total_splits_evenly():
    assert split_cents(0, 3) == [0, 0, 0]


def test_negative_total_mirrors_positive():
    assert split_cents(-10, 3) == [-4, -3, -3]


def test_negative_wider_split_mirrors():
    assert split_cents(-10, 4) == [-3, -3, -2, -2]


def test_zero_parts_rejected():
    with pytest.raises(ValueError):
        split_cents(10, 0)


def test_negative_parts_rejected():
    with pytest.raises(ValueError):
        split_cents(10, -2)


def test_float_total_rejected():
    with pytest.raises(TypeError):
        split_cents(10.5, 2)


def test_float_count_rejected():
    with pytest.raises(TypeError):
        split_cents(10, 2.5)
