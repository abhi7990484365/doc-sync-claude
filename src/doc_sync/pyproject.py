"""Read project metadata from pyproject.toml."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from doc_sync.fs import read_text

PYPROJECT_NAME = "pyproject.toml"


def load_pyproject(root: Path) -> dict[str, Any]:
    """Parse root/pyproject.toml. Return {} if missing, unreadable or invalid."""
    text = read_text(root / PYPROJECT_NAME)
    if text is None:
        return {}
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return {}


def _as_dict(value: Any) -> dict[str, Any]:
    """Return value if it is a dict, else {}."""
    return value if isinstance(value, dict) else {}


def _clean(value: Any) -> str | None:
    """Return the stripped string, or None if not a non-blank str."""
    if not isinstance(value, str):
        return None
    return value.strip() or None


def project_table(data: dict[str, Any]) -> dict[str, Any]:
    """Return the [project] table, or {} if absent or not a table."""
    return _as_dict(data.get("project"))


def project_field(data: dict[str, Any], key: str) -> str | None:
    """Return a non-blank string field of [project], else None."""
    return _clean(project_table(data).get(key))


def project_scripts(data: dict[str, Any]) -> list[str]:
    """Return '<name> = <target>' per valid [project.scripts] entry, in order."""
    entries: list[str] = []
    for name, target in _as_dict(project_table(data).get("scripts")).items():
        clean_name, clean_target = _clean(name), _clean(target)
        if clean_name and clean_target:
            entries.append(f"{clean_name} = {clean_target}")
    return entries
