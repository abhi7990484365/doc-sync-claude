"""Read facts from README.md (FR-5, FR-14, FR-15, FR-16, FR-28)."""

from __future__ import annotations

import re
from pathlib import Path

from doc_sync.fs import read_text
from doc_sync.markdown import Heading, fence_flags, find_headings

README_NAME = "README.md"
_THEMATIC_RE = re.compile(r"^ {0,3}([-*_])(?:[ \t]*\1){2,}[ \t]*$")


def load_readme(root: Path) -> str | None:
    """Return the README.md text under root, or None if missing or unreadable."""
    return read_text(root / README_NAME)


def first_heading(text: str) -> str | None:
    """Return the text of the first ATX or setext heading, else None."""
    headings = find_headings(text.splitlines())
    if not headings or not headings[0].text:
        return None
    return headings[0].text


def _skipped_lines(lines: list[str], headings: list[Heading]) -> list[bool]:
    """Flag lines that cannot be paragraph text: fences, headings, thematic breaks."""
    skipped, _ = fence_flags(lines)
    for heading in headings:
        for index in range(heading.start, heading.end + 1):
            skipped[index] = True
    return [
        flag or bool(_THEMATIC_RE.match(line)) for flag, line in zip(skipped, lines)
    ]


def first_paragraph(text: str) -> str | None:
    """Return the first paragraph (lines joined by single spaces), else None."""
    lines = text.splitlines()
    skipped = _skipped_lines(lines, find_headings(lines))
    run: list[str] = []
    for line, skip in zip(lines, skipped):
        if skip or not line.strip():
            if run:
                break
            continue
        run.append(line.strip())
    return " ".join(run) if run else None


def _matching_heading(headings: list[Heading], titles: tuple[str, ...]) -> Heading | None:
    """Return the first heading (document order) whose text is one of titles."""
    wanted = {title.casefold() for title in titles}
    for heading in headings:
        if heading.text.casefold() in wanted:
            return heading
    return None


def _section_end(lines: list[str], headings: list[Heading], found: Heading) -> int:
    """Return the exclusive end line of the section that starts after `found`."""
    for heading in headings:
        if heading.start > found.end and heading.level <= found.level:
            return heading.start
    return len(lines)


def section_body(text: str, titles: tuple[str, ...]) -> str | None:
    """Return the stripped body of the first heading matching titles, else None.

    The body ends at the next heading of the same or higher level. An empty
    body returns None. Later matching headings are not searched.
    """
    lines = text.splitlines()
    headings = find_headings(lines)
    found = _matching_heading(headings, titles)
    if found is None:
        return None
    end = _section_end(lines, headings, found)
    body = "\n".join(lines[found.end + 1 : end]).strip()
    return body or None
