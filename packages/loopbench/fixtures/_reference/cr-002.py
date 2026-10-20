def mean(xs):
    """Arithmetic mean. Raise ValueError on empty input."""
    if not xs:
        raise ValueError("empty")
    return sum(xs) / len(xs)
