import re


def parse_duration(s):
    """Parse a duration string like '1h30m' into seconds."""
    match = re.fullmatch(r"(\d+)h(?:(\d+)m)?", s)
    if not match:
        return 0
    hours = int(match.group(1))
    return hours * 3600
