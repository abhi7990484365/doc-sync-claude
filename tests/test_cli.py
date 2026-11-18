from pathlib import Path

import pytest

from doc_sync.cli import main, parse_args, path_error, resolve_repo


def test_parse_args_default_cwd(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    assert parse_args([]).repo_path == Path.cwd()


def test_resolve_and_path_error(tmp_path: Path) -> None:
    f = tmp_path / "f.txt"
    f.write_text("x")
    assert resolve_repo(tmp_path) == tmp_path
    assert resolve_repo(f) is None
    assert resolve_repo(tmp_path / "nope") is None
    assert path_error(f) == "REPO_PATH is not a directory"
    assert path_error(tmp_path / "nope") == f"REPO_PATH not found: {tmp_path / 'nope'}"


def test_default_cwd(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    assert main([]) == 0
    assert (tmp_path / "docs" / "PROJECT_DOC.md").is_file()
    assert capsys.readouterr().out.startswith("Wrote ")


def test_explicit_path_empty_repo_has_not_found(tmp_path: Path, capsys) -> None:
    assert main([str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert out.strip() == f"Wrote {tmp_path / 'docs' / 'PROJECT_DOC.md'}"
    assert "Not Found" in (tmp_path / "docs" / "PROJECT_DOC.md").read_text(encoding="utf-8")


def test_missing_path(tmp_path: Path, capsys) -> None:
    missing = tmp_path / "missing"
    assert main([str(missing)]) == 2
    captured = capsys.readouterr()
    assert captured.err.strip() == f"REPO_PATH not found: {missing}"
    assert captured.out == ""
    assert not (missing / "docs").exists()
    assert not (tmp_path / "docs").exists()


def test_file_path(tmp_path: Path, capsys) -> None:
    f = tmp_path / "f.txt"
    f.write_text("x")
    assert main([str(f)]) == 2
    assert capsys.readouterr().err.strip() == "REPO_PATH is not a directory"
    assert not (tmp_path / "docs").exists()


def test_write_failure(tmp_path: Path, capsys) -> None:
    (tmp_path / "docs").write_text("block")
    assert main([str(tmp_path)]) == 1
    err = capsys.readouterr().err
    assert len(err.strip().splitlines()) == 1
    assert "Traceback" not in err


def test_output_has_no_env_values(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys
) -> None:
    monkeypatch.setenv("DOC_SYNC_FAKE_SECRET", "s3cr3t-value-xyz")
    assert main([str(tmp_path)]) == 0
    captured = capsys.readouterr()
    assert "s3cr3t-value-xyz" not in captured.out + captured.err
