"""Packaging checks for FR-1 and NFR-1 (T-1)."""
import tomllib
from pathlib import Path
from typing import Any

PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"


def load_project() -> dict[str, Any]:
    with PYPROJECT.open("rb") as handle:
        return tomllib.load(handle)["project"]


def test_console_script_declared() -> None:
    assert load_project()["scripts"]["doc_sync"] == "doc_sync.cli:main"


def test_python_requirement() -> None:
    assert load_project()["requires-python"] == ">=3.11"


def test_package_importable() -> None:
    import doc_sync

    assert doc_sync.__name__ == "doc_sync"
