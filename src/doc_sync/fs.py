"""Shared safe file helpers."""

from __future__ import annotations

import os
import stat
from pathlib import Path

GIT_DIR = ".git"
OUTPUT_RELATIVE = ("docs", "PROJECT_DOC.md")


def read_text(path: Path) -> str | None:
    """Read a file as UTF-8 (BOM dropped). Return None if missing or unreadable."""
    try:
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return None


def is_dir(path: Path) -> bool:
    """True if path is an existing directory (never raises)."""
    try:
        return Path(path).is_dir()
    except OSError:
        return False


def _is_output_file(root: Path, path: Path) -> bool:
    """True when path is the generated docs/PROJECT_DOC.md under root."""
    return path == root.joinpath(*OUTPUT_RELATIVE)


def _is_link_or_reparse(path: str) -> bool:
    """True for symlinks and NTFS junctions/reparse points (no-op flag on POSIX)."""
    if os.path.islink(path):
        return True
    try:
        attrs = getattr(os.lstat(path), "st_file_attributes", 0)
    except OSError:
        return False
    return bool(attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _walk_dirs(root: Path) -> list[tuple[Path, list[str], list[str]]]:
    """Walk root, pruning .git and ignoring errors; symlinks and junctions are not followed."""
    entries: list[tuple[Path, list[str], list[str]]] = []
    for current, dirnames, filenames in os.walk(root, onerror=lambda _e: None):
        dirnames[:] = [
            d for d in dirnames
            if d != GIT_DIR and not _is_link_or_reparse(os.path.join(current, d))
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
