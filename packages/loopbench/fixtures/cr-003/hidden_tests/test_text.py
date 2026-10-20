from text import slugify
def test_basic(): assert slugify("Hello World") == "hello-world"
def test_punct(): assert slugify("  Hi, there!! ") == "hi-there"
def test_runs(): assert slugify("a  --  b") == "a-b"
