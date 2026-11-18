from __future__ import annotations

from pathlib import Path

from doc_sync.entry_points import collect_entry_points, entry_point_files
from doc_sync.fs import iter_repo_files


def _touch(root: Path, *names: str) -> None:
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")


def test_none_found(tmp_path: Path) -> None:
    _touch(tmp_path, "a.py", "README.md")
    assert entry_point_files(tmp_path, iter_repo_files(tmp_path)) == []


def test_empty_input(tmp_path: Path) -> None:
    assert entry_point_files(tmp_path, []) == []
    assert collect_entry_points(tmp_path, {}, []) == []


def test_nested_and_posix_and_sorted(tmp_path: Path) -> None:
    _touch(tmp_path, "pkg/sub/__main__.py", "main.py", "pkg/main.py", "other.py")
    result = entry_point_files(tmp_path, iter_repo_files(tmp_path))
    assert result == ["main.py", "pkg/main.py", "pkg/sub/__main__.py"]
    assert all("\\" not in item for item in result)


def test_unsorted_input_is_sorted(tmp_path: Path) -> None:
    files = [tmp_path / "z" / "main.py", tmp_path / "a" / "__main__.py"]
    assert entry_point_files(tmp_path, files) == ["a/__main__.py", "z/main.py"]


def test_similar_names_not_matched(tmp_path: Path) -> None:
    files = [tmp_path / "domain.py", tmp_path / "main.pyc", tmp_path / "Main.txt"]
    assert entry_point_files(tmp_path, files) == []


def test_git_dir_excluded(tmp_path: Path) -> None:
    _touch(tmp_path, ".git/main.py", "main.py")
    assert entry_point_files(tmp_path, iter_repo_files(tmp_path)) == ["main.py"]


def test_files_outside_root_ignored(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    files = [tmp_path / "main.py", root / "main.py"]
    assert entry_point_files(root, files) == ["main.py"]


def test_scripts_first_then_files(tmp_path: Path) -> None:
    _touch(tmp_path, "main.py", "pkg/__main__.py")
    data = {"project": {"scripts": {"zed": "z:main", "abc": "a:run"}}}
    result = collect_entry_points(tmp_path, data, iter_repo_files(tmp_path))
    assert result == ["zed = z:main", "abc = a:run", "main.py", "pkg/__main__.py"]


def test_scripts_only(tmp_path: Path) -> None:
    data = {"project": {"scripts": {"tool": "pkg:cli"}}}
    assert collect_entry_points(tmp_path, data, []) == ["tool = pkg:cli"]


def test_files_only_when_no_scripts(tmp_path: Path) -> None:
    _touch(tmp_path, "main.py")
    assert collect_entry_points(tmp_path, {}, iter_repo_files(tmp_path)) == ["main.py"]


def test_no_duplicates(tmp_path: Path) -> None:
    files = [tmp_path / "main.py", tmp_path / "main.py"]
    data = {"project": {"scripts": {"main.py": "x"}}}
    assert collect_entry_points(tmp_path, data, files) == ["main.py = x", "main.py"]
    assert collect_entry_points(tmp_path, {}, files) == ["main.py"]
