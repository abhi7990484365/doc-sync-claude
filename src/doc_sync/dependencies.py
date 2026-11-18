"""Read requirements.txt safely (no credentials, no pip options)."""

from __future__ import annotations

import re
from pathlib import Path

from doc_sync.fs import read_text

REQUIREMENTS_FILE = "requirements.txt"
_URL_USERINFO = re.compile(r"(?<=://)[^/\s]*@")
_INLINE_COMMENT = re.compile(r"\s#.*$")


def strip_url_credentials(text: str) -> str:
    """Remove userinfo (user:pass@ or token@) after any URL scheme."""
    return _URL_USERINFO.sub("", text)


def clean_requirement(line: str) -> str | None:
    """Return a safe requirement string, or None for lines to skip."""
    stripped = line.strip()
    if not stripped or stripped.startswith(("#", "-")):
        return None
    without_comment = _INLINE_COMMENT.sub("", stripped)
    cleaned = strip_url_credentials(without_comment).strip()
    return cleaned or None


def parse_requirements(text: str) -> list[str]:
    """Clean every line of a requirements file, in file order."""
    cleaned = (clean_requirement(line) for line in text.splitlines())
    return [item for item in cleaned if item is not None]


def read_dependencies(root: Path) -> list[str]:
    """Read root/requirements.txt; missing or unreadable file gives []."""
    text = read_text(root / REQUIREMENTS_FILE)
    return [] if text is None else parse_requirements(text)
