from slugs import slugify


def test_spaces_become_hyphens():
    assert slugify("Hello World") == "hello-world"


def test_surrounding_whitespace_ignored():
    assert slugify("  Hello World  ") == "hello-world"


def test_existing_hyphen_kept():
    assert slugify("Hello-World") == "hello-world"


def test_short_text_respects_length_limit():
    assert slugify("Hello", max_length=20) == "hello"


def test_blank_text_stays_blank():
    assert slugify("") == ""


def test_repeated_separators_collapse():
    assert slugify("Hello   World") == "hello-world"
    assert slugify("Hello---World") == "hello-world"


def test_border_hyphens_removed():
    assert slugify("---Hello---") == "hello"


def test_accented_text_becomes_ascii():
    assert slugify("Café au lait") == "cafe-au-lait"


def test_punctuation_is_dropped():
    assert slugify("Hello, World!") == "hello-world"


def test_length_limit_strips_dangling_hyphen():
    assert slugify("Hello World", max_length=6) == "hello"


def test_underscores_become_hyphens():
    assert slugify("Hello_World") == "hello-world"


def test_symbol_only_text_is_blank():
    assert slugify("***") == ""
