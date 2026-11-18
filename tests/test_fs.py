from __future__ import annotations

import os
from pathlib import Path

import pytest

from doc_sync.fs import iter_repo_files, read_text


def test_read_text_plain(tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_text("hello", encoding="utf-8")
    assert read_text(f) == "hello"


def test_read_text_drops_bom(tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_bytes(b"\xef\xbb\xbfhello")
    assert read_text(f) == "hello"


def test_read_text_missing_file(tmp_path: Path) -> None:
    assert read_text(tmp_path / "nope.txt") is None


def test_read_text_directory(tmp_path: Path) -> None:
    assert read_text(tmp_path) is None


def test_read_text_bad_encoding(tmp_path: Path) -> None:
    f = tmp_path / "bad.txt"
    f.write_bytes(b"\xff\xfe\x00bad\x80")
    assert read_text(f) is None


def test_iter_empty_repo(tmp_path: Path) -> None:
    assert iter_repo_files(tmp_path) == []


def test_iter_missing_root(tmp_path: Path) -> None:
    assert iter_repo_files(tmp_path / "missing") == []


def test_iter_prunes_git(tmp_path: Path) -> None:
    (tmp_path / ".git" / "objects").mkdir(parents=True)
    (tmp_path / ".git" / "objects" / "x.py").write_text("x")
    (tmp_path / "a.py").write_text("a")
    assert iter_repo_files(tmp_path) == [tmp_path / "a.py"]


def test_iter_skips_output_file_only(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "PROJECT_DOC.md").write_text("x")
    (tmp_path / "docs" / "other.md").write_text("y")
    (tmp_path / "sub" / "docs").mkdir(parents=True)
    (tmp_path / "sub" / "docs" / "PROJECT_DOC.md").write_text("z")
    assert iter_repo_files(tmp_path) == [
        tmp_path / "docs" / "other.md",
        tmp_path / "sub" / "docs" / "PROJECT_DOC.md",
    ]


def test_iter_sorted(tmp_path: Path) -> None:
    for rel in ("b.py", "a/z.py", "a/b.py", "c/d/e.py"):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("")
    result = iter_repo_files(tmp_path)
    assert result == sorted(result)
    assert len(result) == 4


def test_iter_skips_symlinked_dirs(tmp_path: Path) -> None:
    target = tmp_path / "real"
    target.mkdir()
    (target / "f.py").write_text("")
    link = tmp_path / "link"
    try:
        os.symlink(target, link, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not available")
    assert iter_repo_files(tmp_path) == [target / "f.py"]


def _make_junction(link: Path, target: Path) -> None:
    import subprocess

    try:
        import _winapi  # type: ignore[import-not-found]

        _winapi.CreateJunction(str(target), str(link))
        return
    except (ImportError, AttributeError, OSError):
        pass
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(target)],
        capture_output=True, check=False,
    )
    if result.returncode != 0:
        pytest.skip("junctions not available")


@pytest.mark.skipif(os.name != "nt", reason="NTFS junctions are Windows-only")
def test_iter_skips_junctions(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.py").write_text("")
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "a.py").write_text("")
    _make_junction(repo / "jlink", outside)
    _make_junction(repo / "loop", repo)
    assert iter_repo_files(repo) == [repo / "a.py"]


@pytest.mark.skipif(os.name == "nt", reason="chmod 000 is not enforced on Windows")
@pytest.mark.skipif(hasattr(os, "geteuid") and os.geteuid() == 0, reason="root reads all")
def test_iter_unreadable_dir_ignored(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("")
    locked = tmp_path / "locked"
    locked.mkdir()
    (locked / "b.py").write_text("")
    locked.chmod(0)
    try:
        assert iter_repo_files(tmp_path) == [tmp_path / "a.py"]
    finally:
        locked.chmod(0o700)


def test_iter_walk_error_is_ignored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from doc_sync import fs

    def fake_walk(root: object, onerror: object = None):
        onerror(OSError("denied"))  # type: ignore[misc]
        yield str(tmp_path), [], ["a.py"]

    monkeypatch.setattr(fs.os, "walk", fake_walk)
    assert iter_repo_files(tmp_path) == [tmp_path / "a.py"]
