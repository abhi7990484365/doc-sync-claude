from pathlib import Path

from doc_sync.pyproject import (
    load_pyproject,
    project_field,
    project_scripts,
    project_table,
)

VALID = """
[project]
name = "demo"
description = "A demo"

[project.scripts]
zeta = "pkg.z:main"
alpha = "pkg.a:main"
"""


def _write(tmp_path: Path, text: str) -> None:
    (tmp_path / "pyproject.toml").write_text(text, encoding="utf-8")


def test_valid_file(tmp_path: Path) -> None:
    _write(tmp_path, VALID)
    data = load_pyproject(tmp_path)
    assert project_field(data, "name") == "demo"
    assert project_field(data, "description") == "A demo"
    assert project_table(data)["name"] == "demo"


def test_scripts_declared_order(tmp_path: Path) -> None:
    _write(tmp_path, VALID)
    assert project_scripts(load_pyproject(tmp_path)) == [
        "zeta = pkg.z:main",
        "alpha = pkg.a:main",
    ]


def test_missing_file(tmp_path: Path) -> None:
    assert load_pyproject(tmp_path) == {}


def test_invalid_toml(tmp_path: Path) -> None:
    _write(tmp_path, "[project\nname = ")
    assert load_pyproject(tmp_path) == {}


def test_project_not_table() -> None:
    data = {"project": "oops"}
    assert project_table(data) == {}
    assert project_field(data, "name") is None
    assert project_scripts(data) == []


def test_no_project() -> None:
    assert project_table({}) == {}
    assert project_field({}, "name") is None
    assert project_scripts({}) == []


def test_scripts_not_table() -> None:
    assert project_scripts({"project": {"scripts": ["a"]}}) == []


def test_scripts_skip_bad_entries() -> None:
    scripts = {"ok": "m:f", "num": 5, "empty": "", "blank": "  ", 1: "x", " ": "m:f"}
    assert project_scripts({"project": {"scripts": scripts}}) == ["ok = m:f"]


def test_field_non_string_or_blank() -> None:
    data = {"project": {"name": "  ", "description": 3, "version": "  1.0 "}}
    assert project_field(data, "name") is None
    assert project_field(data, "description") is None
    assert project_field(data, "missing") is None
    assert project_field(data, "version") == "1.0"
