import re
import unicodedata


def slugify(text, max_length=None):
    """Lowercase ASCII slug. Separator runs collapse to one hyphen."""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    if max_length is not None:
        slug = slug[:max_length].rstrip("-")
    return slug
