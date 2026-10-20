import re
def slugify(s):
    """Lowercase, trim, collapse runs of non-alphanumerics to single '-', no leading/trailing '-'."""
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
