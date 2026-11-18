"""collect(root) assembles ProjectInfo without raising or inventing values."""

import dataclasses
from pathlib import Path

import pytest

from doc_sync import collect as collect_module
from doc_sync.collect import ProjectInfo, collect

EMPTY = ProjectInfo(None, None, [], [], [], None, None)


def test_empty_dir_gives_all_missing(tmp_path: Path) -> None:
    assert collect(tmp_path) == EMPTY


def test_missing_root(tmp_path: Path) -> None:
    assert collect(tmp_path / "nope") == EMPTY


def test_root_is_file(tmp_path: Path) -> None:
    f = tmp_path / "f.txt"
    f.write_text("x", encoding="utf-8")
    assert collect(f) == EMPTY


def test_frozen() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        EMPTY.name = "x"  # type: ignore[misc]


def test_readme_only(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        "# Proj\n\nDoes things.\n\n## Usage\n\nrun it\n", encoding="utf-8"
    )
    info = collect(tmp_path)
    assert info.name == "Proj"
    assert info.description == "Does things."
    assert info.how_to_run == "run it"
    assert info.dependencies == [] and info.entry_points == []


def test_full_assembly(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "n"\n[project.scripts]\ncli = "pkg:main"\n', encoding="utf-8"
    )
    (tmp_path / "requirements.txt").write_text("requests>=2\n", encoding="utf-8")
    (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "main.py").write_text("x = 1\n", encoding="utf-8")
    info = collect(tmp_path)
    assert info.languages == ["Python"]
    assert info.dependencies == ["requests>=2"]
    assert info.entry_points == ["cli = pkg:main", "main.py"]
    assert info.how_to_run is None


def test_no_invented_values_without_usage(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("# T\n\nText.\n", encoding="utf-8")
    assert collect(tmp_path).how_to_run is None


def test_last_commit_failure_gives_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(collect_module, "last_commit", lambda _root: None)
    assert collect(tmp_path).last_commit is None


def test_not_a_git_repo_gives_none(tmp_path: Path) -> None:
    assert collect(tmp_path).last_commit is None


def test_unreadable_readme_does_not_raise(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_bytes(b"\xff\xfe\x00bad")
    assert collect(tmp_path).name is None
