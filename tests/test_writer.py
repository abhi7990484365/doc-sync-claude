from __future__ import annotations

import os
from pathlib import Path

import pytest

from doc_sync import writer
from doc_sync.writer import atomic_write, write_doc


def test_creates_docs_dir(tmp_path: Path) -> None:
    out = write_doc(tmp_path, "hello\n")
    assert out == tmp_path / "docs" / "PROJECT_DOC.md"
    assert out.read_text(encoding="utf-8") == "hello\n"


def test_overwrites_existing(tmp_path: Path) -> None:
    write_doc(tmp_path, "old\n")
    out = write_doc(tmp_path, "new\n")
    assert out.read_text(encoding="utf-8") == "new\n"


def test_identical_on_rerun(tmp_path: Path) -> None:
    out = write_doc(tmp_path, "same\nlines\n")
    first = out.read_bytes()
    write_doc(tmp_path, "same\nlines\n")
    assert out.read_bytes() == first
    assert b"\r" not in first


def test_docs_is_file(tmp_path: Path) -> None:
    (tmp_path / "docs").write_text("x", encoding="utf-8")
    with pytest.raises(OSError):
        write_doc(tmp_path, "t")


def test_target_is_directory_no_temp_left(tmp_path: Path) -> None:
    target_dir = tmp_path / "docs" / "PROJECT_DOC.md"
    target_dir.mkdir(parents=True)
    with pytest.raises(OSError):
        write_doc(tmp_path, "t")
    assert [p.name for p in (tmp_path / "docs").iterdir()] == ["PROJECT_DOC.md"]


def test_existing_unchanged_when_replace_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = write_doc(tmp_path, "keep\n")

    def boom(src: object, dst: object) -> None:
        raise OSError("boom")

    monkeypatch.setattr(writer.os, "replace", boom)
    with pytest.raises(OSError):
        atomic_write(out, "changed\n")
    monkeypatch.undo()
    assert out.read_text(encoding="utf-8") == "keep\n"
    assert [p.name for p in out.parent.iterdir()] == ["PROJECT_DOC.md"]


def test_non_ascii_round_trip(tmp_path: Path) -> None:
    text = "café 日本語 ✓\n"
    out = write_doc(tmp_path, text)
    assert out.read_text(encoding="utf-8") == text


def test_unencodable_char_replaced(tmp_path: Path) -> None:
    out = write_doc(tmp_path, "a\ud800b\n")
    assert out.read_text(encoding="utf-8") == "a?b\n"
    assert os.path.exists(out)
