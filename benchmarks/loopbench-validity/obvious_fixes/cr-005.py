def merge_intervals(intervals):
    """Merge overlapping (start, end) intervals into disjoint ranges."""
    merged = []
    for start, end in intervals:
        if not merged or start >= merged[-1][1]:
            merged.append((start, end))
        else:
            merged[-1] = (merged[-1][0], end)
    return merged
