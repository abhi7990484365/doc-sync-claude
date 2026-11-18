"""Markdown output and the single `Not Found` rule (FR-3, FR-4, FR-9, FR-10, FR-28)."""

from __future__ import annotations

from typing import Final

from doc_sync.collect import ProjectInfo
from doc_sync.markdown import atx_heading, fence_flags, setext_level

NOT_FOUND: Final = "Not Found"
SECTION_ORDER: Final[tuple[str, ...]] = (
    "Name",
    "Description",
    "Languages",
    "Dependencies",
    "Entry Points",
    "How to Run",
    "Last Commit",
)
_MAX_DEMOTED_LEVEL: Final = 2


def single_line(value: str) -> str:
    """Collapse all whitespace runs, including newlines, into single spaces."""
    return " ".join(value.split())


def _demote(line: str) -> str:
    """Turn a level 1 or 2 ATX heading line into a level 3 heading."""
    heading = atx_heading(line)
    if heading is None or heading[0] > _MAX_DEMOTED_LEVEL:
        return line
    return f"### {heading[1]}".rstrip()


def _is_text_line(line: str, in_fence: bool) -> bool:
    """True for a non-blank line that is outside fences and not a heading."""
    return bool(line.strip()) and not in_fence and atx_heading(line) is None


def _safe_lines(lines: list[str], flags: list[bool]) -> list[str]:
    """Demote headings and escape setext underlines outside fences."""
    result: list[str] = []
    for index, line in enumerate(lines):
        if flags[index]:
            result.append(line)
        elif setext_level(line) is not None and index > 0 and _is_text_line(
            lines[index - 1], flags[index - 1]
        ):
            result.append("\\" + line.lstrip())
        else:
            result.append(_demote(line))
    return result


def safe_body(text: str) -> str:
    """Make free text safe to place under a level-2 section."""
    lines = text.splitlines()
    flags, open_marker = fence_flags(lines)
    result = _safe_lines(lines, flags)
    if open_marker is not None:
        result.append(open_marker)
    return "\n".join(result).strip()


def render_text(value: str | None) -> str:
    """Render a scalar body, or `Not Found` when it is missing or blank."""
    if not isinstance(value, str) or not value.strip():
        return NOT_FOUND
    return safe_body(value) or NOT_FOUND


def render_list(items: list[str]) -> str:
    """Render `- item` lines, or `Not Found` for an empty list."""
    cleaned = [single_line(item) for item in items if isinstance(item, str)]
    lines = [f"- {item}" for item in cleaned if item]
    return "\n".join(lines) if lines else NOT_FOUND


def _render_name(name: str | None) -> str:
    """Render the one-line name used by the title and the Name section."""
    if not isinstance(name, str):
        return NOT_FOUND
    return single_line(name) or NOT_FOUND


def _section(title: str, body: str) -> str:
    """Build one level-2 section."""
    return f"## {title}\n\n{body}\n"


def render_document(info: ProjectInfo) -> str:
    """Build the full PROJECT_DOC.md text with one trailing newline."""
    name = _render_name(info.name)
    bodies = (
        name,
        render_text(info.description),
        render_list(info.languages),
        render_list(info.dependencies),
        render_list(info.entry_points),
        render_text(info.how_to_run),
        render_text(info.last_commit),
    )
    sections = [_section(t, b) for t, b in zip(SECTION_ORDER, bodies, strict=True)]
    return f"# {name}\n\n" + "\n".join(sections)
