"""Shared Markdown line rules: headings and fences (FR-28)."""

from __future__ import annotations

import re
from typing import NamedTuple

_FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
_ATX_RE = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+|$)(.*)")
_CLOSING_HASHES_RE = re.compile(r"(?:^|[ \t]+)#+[ \t]*$")
_SETEXT_1_RE = re.compile(r"^ {0,3}=+\s*$")
_SETEXT_2_RE = re.compile(r"^ {0,3}-+\s*$")


class Heading(NamedTuple):
    """A heading. `start` and `end` are 0-based line indexes, both inclusive.

    ATX headings have start == end. Setext headings span the text run and the
    underline line.
    """

    start: int
    end: int
    level: int
    text: str


def atx_heading(line: str) -> tuple[int, str] | None:
    """Return (level, text) for an ATX heading line, else None."""
    match = _ATX_RE.match(line)
    if match is None:
        return None
    text = _CLOSING_HASHES_RE.sub("", match.group(2).strip()).strip()
    return len(match.group(1)), text


def setext_level(line: str) -> int | None:
    """Return 1 for a `===` underline, 2 for a `---` underline, else None."""
    if _SETEXT_1_RE.match(line):
        return 1
    if _SETEXT_2_RE.match(line):
        return 2
    return None


def _closes(line: str, marker: str) -> bool:
    """True if `line` closes a fence opened with `marker`."""
    stripped = line.strip()
    return (
        bool(_FENCE_RE.match(line))
        and stripped[0] == marker[0]
        and set(stripped) == {marker[0]}
        and len(stripped) >= len(marker)
    )


def fence_flags(lines: list[str]) -> tuple[list[bool], str | None]:
    """Flag fence lines and lines inside fences.

    Returns the flags and the opening marker of a fence still open at the end
    (else None).
    """
    flags: list[bool] = []
    marker: str | None = None
    for line in lines:
        if marker is None:
            match = _FENCE_RE.match(line)
            if match:
                marker = match.group(1)
            flags.append(match is not None)
        else:
            flags.append(True)
            if _closes(line, marker):
                marker = None
    return flags, marker


def find_headings(lines: list[str]) -> list[Heading]:
    """Find ATX and setext headings outside fences, in document order."""
    flags, _ = fence_flags(lines)
    headings: list[Heading] = []
    run: list[str] = []
    run_start = 0
    for index, line in enumerate(lines):
        atx = None if flags[index] else atx_heading(line)
        underline = None if flags[index] else setext_level(line)
        if flags[index] or not line.strip():
            run = []
        elif atx is not None:
            headings.append(Heading(index, index, atx[0], atx[1]))
            run = []
        elif underline is not None and run:
            text = " ".join(part.strip() for part in run)
            headings.append(Heading(run_start, index, underline, text))
            run = []
        elif underline == 2:
            run = []  # thematic break, not text
        else:
            if not run:
                run_start = index
            run.append(line)
    return headings
