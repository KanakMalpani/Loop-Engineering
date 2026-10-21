def split_cents(total, n):
    """Split a cent total into n integer parts."""
    part = total // n
    return [part] * n
