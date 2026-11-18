from __future__ import annotations

from pathlib import Path

from doc_sync.readme import first_heading, first_paragraph, load_readme, section_body

TITLES = ("Usage", "How to Run")


def test_load_missing(tmp_path: Path) -> None:
    assert load_readme(tmp_path) is None


def test_load_empty(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("", encoding="utf-8")
    assert load_readme(tmp_path) == ""


def test_load_bom_dropped(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_bytes(b"\xef\xbb\xbf# Title\n")
    text = load_readme(tmp_path)
    assert text == "# Title\n"
    assert first_heading(text) == "Title"


def test_empty_text() -> None:
    assert first_heading("") is None
    assert first_paragraph("") is None
    assert section_body("", TITLES) is None


def test_first_heading_atx() -> None:
    assert first_heading("intro\n\n# Name\n## Other\n") == "Name"


def test_first_heading_setext() -> None:
    assert first_heading("My Project\n==========\n") == "My Project"


def test_heading_in_fence_ignored() -> None:
    assert first_heading("```\n# Fake\n```\n\n# Real\n") == "Real"
    assert first_heading("```\n# Fake\n```\n") is None


def test_first_paragraph_skips_headings() -> None:
    text = "# Title\n\nFirst line\nsecond line\n\nOther\n"
    assert first_paragraph(text) == "First line second line"


def test_first_paragraph_heading_directly_followed_by_text() -> None:
    assert first_paragraph("# Title\nBody text\n\nMore\n") == "Body text"


def test_first_paragraph_skips_setext_fence_and_break() -> None:
    text = "Title\n=====\n\n```\ncode\n```\n\n---\n\nReal text\n"
    assert first_paragraph(text) == "Real text"


def test_first_paragraph_none_when_only_headings() -> None:
    assert first_paragraph("# A\n\n## B\n") is None


def test_section_body_basic_case_insensitive() -> None:
    text = "# T\n\n## usage\n\nrun it\n\n## Other\nx\n"
    assert section_body(text, TITLES) == "run it"


def test_section_body_how_to_run() -> None:
    assert section_body("## How to Run\npython x.py\n", TITLES) == "python x.py"


def test_section_body_first_match_in_document_order() -> None:
    text = "## How to Run\nfirst\n\n## Usage\nsecond\n"
    assert section_body(text, TITLES) == "first"


def test_section_body_empty_first_match_gives_none() -> None:
    text = "## Usage\n\n## How to Run\nlater\n"
    assert section_body(text, TITLES) is None


def test_section_body_absent() -> None:
    assert section_body("# T\n\n## Install\nx\n", TITLES) is None


def test_section_ends_at_same_or_higher_level() -> None:
    text = "## Usage\na\n### Sub\nb\n# Top\nc\n"
    assert section_body(text, TITLES) == "a\n### Sub\nb"
    assert section_body("### Usage\na\n## Higher\nb\n", TITLES) == "a"


def test_section_fence_heading_does_not_end_section() -> None:
    text = "## Usage\n```\n## not a heading\n```\n## End\n"
    assert section_body(text, TITLES) == "```\n## not a heading\n```"


def test_section_setext_heading_ends_section() -> None:
    text = "## Usage\nrun\n\nNext\n----\nz\n"
    assert section_body(text, TITLES) == "run"


def test_section_heading_in_fence_not_matched() -> None:
    assert section_body("```\n## Usage\nx\n```\n", TITLES) is None
