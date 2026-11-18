"""Collect entry points from pyproject scripts and well-known files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from doc_sync.pyproject import project_scripts

ENTRY_FILE_NAMES: frozenset[str] = frozenset({"__main__.py", "main.py"})


def _relative_posix(root: Path, path: Path) -> str | None:
    """Return the repo-relative POSIX path, or None if outside the root."""
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return None


def entry_point_files(root: Path, files: list[Path]) -> list[str]:
    """Return sorted repo-relative POSIX paths of `__main__.py`/`main.py`."""
    found = {
        rel
        for path in files
        if path.name in ENTRY_FILE_NAMES
        and (rel := _relative_posix(root, path)) is not None
    }
    return sorted(found)


def collect_entry_points(
    root: Path, data: dict[str, Any], files: list[Path]
) -> list[str]:
    """Return pyproject scripts first, then entry files, without duplicates."""
    combined = [*project_scripts(data), *entry_point_files(root, files)]
    return list(dict.fromkeys(combined))
