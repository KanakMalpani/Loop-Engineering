def split_cents(total, n):
    """Split a cent total into n integer parts."""
    part = total // n
    parts = [part] * n
    remainder = total - part * n
    for index in range(remainder):
        parts[-1 - index] += 1
    return parts
