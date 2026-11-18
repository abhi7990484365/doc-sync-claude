"""Read requirements.txt safely (no credentials, no pip options)."""

from __future__ import annotations

import re
from pathlib import Path

from doc_sync.fs import read_text

REQUIREMENTS_FILE = "requirements.txt"
_URL_USERINFO = re.compile(r"(?<=://)[^/\s]*@")
_URL_QUERY = re.compile(r"(://[^\s?]*)\?\S*")
_HASH_OPTION = re.compile(r"\s--hash(?:=|\s)\S*")
_INLINE_COMMENT = re.compile(r"\s#.*$")


def strip_url_credentials(text: str) -> str:
    """Remove userinfo and the whole `?query` part of any URL."""
    return _URL_QUERY.sub(r"\1", _URL_USERINFO.sub("", text))


def join_continuations(text: str) -> list[str]:
    """Join lines ending in a backslash with the following line."""
    lines: list[str] = []
    pending = ""
    for raw in text.splitlines():
        if raw.rstrip().endswith("\\"):
            pending += raw.rstrip()[:-1] + " "
            continue
        lines.append(pending + raw)
        pending = ""
    if pending:
        lines.append(pending)
    return lines


def clean_requirement(line: str) -> str | None:
    """Return a safe requirement string, or None for lines to skip."""
    stripped = line.strip()
    if not stripped or stripped.startswith(("#", "-")):
        return None
    without_comment = _INLINE_COMMENT.sub("", stripped)
    without_hashes = _HASH_OPTION.sub("", " " + without_comment)
    cleaned = strip_url_credentials(without_hashes).strip()
    return cleaned or None


def parse_requirements(text: str) -> list[str]:
    """Clean every logical line of a requirements file, in file order."""
    cleaned = (clean_requirement(line) for line in join_continuations(text))
    return [item for item in cleaned if item is not None]


def read_dependencies(root: Path) -> list[str]:
    """Read root/requirements.txt; missing or unreadable file gives []."""
    text = read_text(root / REQUIREMENTS_FILE)
    return [] if text is None else parse_requirements(text)
