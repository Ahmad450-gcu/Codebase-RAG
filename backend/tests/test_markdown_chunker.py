from app.chunking.markdown_chunker import chunk_markdown_file

def test_single_top_level_header():
    doc = "# Title\n\nSome intro text.\n"
    chunks = chunk_markdown_file("r.md", doc)
    sections = [c for c in chunks if c.chunk_type == "section"]
    assert len(sections) == 1
    assert sections[0].name == "Title"
    assert "Some intro text." in sections[0].source

def test_nested_headers_split_to_deepest_level():
    doc = """# Project

## Getting Started

### Installation

#### Docker

Run docker compose up.
"""
    chunks = chunk_markdown_file("r.md", doc)
    sections = {c.name: c for c in chunks if c.chunk_type == "section"}
    assert set(sections.keys()) == {"Project", "Getting Started", "Installation", "Docker"}
    assert "Run docker compose up." in sections["Docker"].source
    assert "Run docker compose up." not in sections["Installation"].source  # no duplication

def test_header_path_breadcrumb_is_correct():
    doc = "# Project\n\n## Getting Started\n\n### Docker\n\nRun it.\n"
    chunks = chunk_markdown_file("r.md", doc)
    docker_section = next(c for c in chunks if c.name == "Docker")
    assert docker_section.metadata["header_path"] == ["Project", "Getting Started", "Docker"]

def test_sibling_headers_do_not_nest():
    doc = "# Project\n\n## Installation\n\nStep 1.\n\n## Usage\n\nStep 2.\n"
    chunks = chunk_markdown_file("r.md", doc)
    usage = next(c for c in chunks if c.name == "Usage")
    assert usage.metadata["header_path"] == ["Project", "Usage"]  # not ["Project", "Installation", "Usage"]

def test_hash_inside_fenced_code_block_is_not_a_header():
    doc = '''# Project

```python
# this is a python comment, not a markdown header
def foo():
    pass
```

## Real Section
'''
    chunks = chunk_markdown_file("r.md", doc)
    sections = [c for c in chunks if c.chunk_type == "section"]
    assert {s.name for s in sections} == {"Project", "Real Section"}
    project = next(s for s in sections if s.name == "Project")
    assert "# this is a python comment" in project.source  # preserved as plain text, not parsed as a header

def test_preamble_before_first_header_is_captured():
    doc = "Some text before any header.\n\n# First Header\n\nContent.\n"
    chunks = chunk_markdown_file("r.md", doc)
    preambles = [c for c in chunks if c.chunk_type == "preamble"]
    assert len(preambles) == 1
    assert "Some text before any header" in preambles[0].source

def test_file_with_no_headers_produces_only_preamble():
    doc = "Just a plain text file with no headers at all.\n"
    chunks = chunk_markdown_file("r.md", doc)
    assert len(chunks) == 1
    assert chunks[0].chunk_type == "preamble"