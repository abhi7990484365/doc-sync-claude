"""Shared safe file helpers."""

from __future__ import annotations

import os
from pathlib import Path

GIT_DIR = ".git"
OUTPUT_RELATIVE = ("docs", "PROJECT_DOC.md")


def read_text(path: Path) -> str | None:
    """Read a file as UTF-8 (BOM dropped). Return None if missing or unreadable."""
    try:
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return None


def _is_output_file(root: Path, path: Path) -> bool:
    """True when path is the generated docs/PROJECT_DOC.md under root."""
    return path == root.joinpath(*OUTPUT_RELATIVE)


def _walk_dirs(root: Path) -> list[tuple[Path, list[str], list[str]]]:
    """Walk root, pruning .git and ignoring errors; symlinked dirs are not followed."""
    entries: list[tuple[Path, list[str], list[str]]] = []
    for current, dirnames, filenames in os.walk(root, onerror=lambda _e: None):
        dirnames[:] = [
            d for d in dirnames
            if d != GIT_DIR and not os.path.islink(os.path.join(current, d))
        ]
        entries.append((Path(current), dirnames, filenames))
    return entries


def iter_repo_files(root: Path) -> list[Path]:
    """Return all files under root, sorted, skipping .git and the output file."""
    files = [
        Path(current) / name
        for current, _dirs, names in _walk_dirs(root)
        for name in names
    ]
    return sorted(p for p in files if not _is_output_file(root, p))
