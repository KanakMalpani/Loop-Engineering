def slugify(text, max_length=None):
    """Turn text into a slug. Spaces should become hyphens."""
    slug = text.lower().strip()
    if max_length is not None:
        slug = slug[:max_length]
    return slug
