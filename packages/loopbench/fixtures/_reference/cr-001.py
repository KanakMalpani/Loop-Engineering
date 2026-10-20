def parse_int(s):
    """Parse a base-10 integer string. Raise ValueError on invalid input."""
    if not isinstance(s, str):
        raise ValueError("not a string")
    return int(s.strip())
