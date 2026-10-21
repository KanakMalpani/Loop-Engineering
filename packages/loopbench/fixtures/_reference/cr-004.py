import re

_UNIT_SECONDS = {"h": 3600, "m": 60, "s": 1}


def parse_duration(s):
    """Parse a duration string like '1h30m' into seconds.

    Units h, m, and s are case-insensitive and may appear in any order.
    Surrounding whitespace is ignored. Empty, repeated-unit, and other
    invalid input raises ValueError.
    """
    try:
        text = s.strip()
    except AttributeError:
        raise ValueError("duration must be a string") from None
    if not text:
        raise ValueError("empty duration")
    if not re.fullmatch(r"(?:\d+[hmsHMS])+", text):
        raise ValueError("invalid duration")
    seen = set()
    total = 0
    for amount, unit in re.findall(r"(\d+)([hmsHMS])", text):
        key = unit.lower()
        if key in seen:
            raise ValueError("repeated unit")
        seen.add(key)
        total += int(amount) * _UNIT_SECONDS[key]
    return total
