from __future__ import annotations

import pytest

from doc_sync.collect import ProjectInfo
from doc_sync.markdown import find_headings
from doc_sync.render import (
    NOT_FOUND,
    SECTION_ORDER,
    render_document,
    render_list,
    render_text,
    safe_body,
    single_line,
)


def _headings(text: str, level: int) -> list[str]:
    return [h.text for h in find_headings(text.splitlines()) if h.level == level]


def test_constants() -> None:
    assert NOT_FOUND == "Not Found"
    assert len(SECTION_ORDER) == 7
    assert SECTION_ORDER[0] == "Name" and SECTION_ORDER[-1] == "Last Commit"


def test_single_line() -> None:
    assert single_line("a\n  b\t\nc ") == "a b c"


def test_render_text_missing() -> None:
    assert render_text(None) == "Not Found"
    assert render_text("  \n ") == "Not Found"
    assert render_text("hello") == "hello"


def test_render_list() -> None:
    assert render_list([]) == "Not Found"
    assert render_list(["", "  "]) == "Not Found"
    assert render_list(["a", "b\nc"]) == "- a\n- b c"


def test_safe_body_demotes_headings() -> None:
    out = safe_body("# One\ntext\n## Two\n### Three\n#### Four")
    assert out.splitlines() == ["### One", "text", "### Two", "### Three", "#### Four"]


def test_safe_body_escapes_setext() -> None:
    out = safe_body("Title\n=====\nOther\n-----")
    assert out.splitlines() == ["Title", "\\=====", "Other", "\\-----"]
    assert find_headings(out.splitlines()) == []


def test_safe_body_keeps_fenced_content() -> None:
    text = "```\n# comment\nx\n---\n```"
    assert safe_body(text) == text


def test_safe_body_closes_unclosed_fence() -> None:
    out = safe_body("```python\n# not heading")
    assert out.splitlines()[-1] == "```"
    out = safe_body("~~~~\ncode")
    assert out.splitlines()[-1] == "~~~~"


def test_thematic_break_after_blank_kept() -> None:
    assert safe_body("a\n\n---\nb") == "a\n\n---\nb"


def test_full_document() -> None:
    info = ProjectInfo(
        name="Demo",
        description="A demo",
        languages=["Python"],
        dependencies=["requests"],
        entry_points=["demo = demo:main"],
        how_to_run="python -m demo",
        last_commit="abc1234 2026-01-01 init",
    )
    out = render_document(info)
    assert out.startswith("# Demo\n")
    assert out.endswith("init\n") and not out.endswith("\n\n")
    assert _headings(out, 1) == ["Demo"]
    assert _headings(out, 2) == list(SECTION_ORDER)
    assert "## Languages\n\n- Python\n" in out
    assert "## Last Commit\n\nabc1234 2026-01-01 init\n" in out


def test_all_none() -> None:
    out = render_document(ProjectInfo())
    assert out.startswith("# Not Found\n")
    assert _headings(out, 2) == list(SECTION_ORDER)
    assert out.count("\nNot Found\n") == 7
    assert out.endswith("\n") and not out.endswith("\n\n")


def test_multiline_name_collapsed() -> None:
    out = render_document(ProjectInfo(name="My\n# Evil\nName"))
    assert out.startswith("# My # Evil Name\n")
    assert _headings(out, 1) == ["My # Evil Name"]


def test_embedded_headings_keep_seven_sections() -> None:
    info = ProjectInfo(
        description="# Top\n## Sub\nText\n=====\n```\nopen",
        how_to_run="## Run\nx",
    )
    out = render_document(info)
    assert _headings(out, 1) == [NOT_FOUND]
    assert _headings(out, 2) == list(SECTION_ORDER)


def test_deterministic() -> None:
    info = ProjectInfo(name="X", description="a\n## b")
    assert render_document(info) == render_document(info)


def test_no_env_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DOC_SYNC_FAKE_TOKEN", "s3cr3t-value-123")
    out = render_document(ProjectInfo(name="X"))
    assert "s3cr3t-value-123" not in out
