import pytest
from stats import mean
def test_basic(): assert mean([1, 2, 3]) == 2
def test_float(): assert mean([1.5, 2.5]) == 2.0
def test_empty():
    with pytest.raises(ValueError): mean([])
