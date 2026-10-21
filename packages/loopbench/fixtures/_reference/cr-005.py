def merge_intervals(intervals):
    """Merge overlapping and touching (start, end) intervals into a new list."""
    cleaned = []
    for start, end in intervals:
        if start > end:
            raise ValueError("start is after end")
        cleaned.append((start, end))
    cleaned.sort()
    merged = []
    for start, end in cleaned:
        if not merged or start > merged[-1][1]:
            merged.append((start, end))
        else:
            prev_start, prev_end = merged[-1]
            merged[-1] = (prev_start, max(prev_end, end))
    return merged
