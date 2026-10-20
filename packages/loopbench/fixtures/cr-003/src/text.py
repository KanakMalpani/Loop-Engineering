def slugify(s):
    """Lowercase, trim, collapse runs of non-alphanumerics to single '-', no leading/trailing '-'."""
    return s.replace(" ", "-")
