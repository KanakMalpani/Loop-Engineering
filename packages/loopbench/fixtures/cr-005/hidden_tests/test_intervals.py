import pytest
from intervals import merge_intervals


def test_disjoint_ranges_stay_separate():
    assert merge_intervals([(1, 2), (4, 5)]) == [(1, 2), (4, 5)]


def test_overlapping_pair_combines():
    assert merge_intervals([(1, 4), (3, 6)]) == [(1, 6)]


def test_chain_of_overlaps_combines():
    assert merge_intervals([(1, 3), (2, 5), (4, 8)]) == [(1, 8)]


def test_unsorted_input_is_merged():
    assert merge_intervals([(8, 10), (1, 4), (3, 6)]) == [(1, 6), (8, 10)]


def test_touching_ranges_combine():
    assert merge_intervals([(1, 2), (2, 5), (5, 6)]) == [(1, 6)]


def test_nested_range_is_absorbed():
    assert merge_intervals([(1, 10), (2, 3), (4, 5)]) == [(1, 10)]


def test_input_list_is_not_mutated():
    original = [(8, 10), (1, 2)]
    snapshot = [(8, 10), (1, 2)]
    merge_intervals(original)
    assert original == snapshot


def test_empty_input_returns_empty():
    assert merge_intervals([]) == []


def test_reversed_bounds_rejected():
    with pytest.raises(ValueError):
        merge_intervals([(1, 4), (6, 2)])


def test_single_range_unchanged():
    assert merge_intervals([(2, 5)]) == [(2, 5)]


def test_negative_bounds_overlap():
    assert merge_intervals([(-5, -1), (-3, 2)]) == [(-5, 2)]
