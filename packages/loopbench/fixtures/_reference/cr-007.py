def split_cents(total, n):
    """Split total cents into n ints. Remainder goes to the earliest parts.

    Negative totals mirror the positive split. n <= 0 raises ValueError.
    Non-integers raise TypeError.
    """
    if not isinstance(total, int) or not isinstance(n, int):
        raise TypeError("total and n must be integers")
    if n <= 0:
        raise ValueError("n must be positive")
    sign = -1 if total < 0 else 1
    amount = abs(total)
    base, extra = divmod(amount, n)
    return [sign * (base + (1 if i < extra else 0)) for i in range(n)]
