def parse_int(s):
    """Parse a base-10 integer string. Raise ValueError on invalid input."""
    try:
        return int(s.strip())
    except (ValueError, AttributeError):
        return None
