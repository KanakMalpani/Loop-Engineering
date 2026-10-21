def merge_intervals(intervals):
    """Merge overlapping (start, end) intervals into disjoint ranges."""
    return [(start, end) for start, end in intervals]
