"""Tests for git_info: find_git, git_env, run_git."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from doc_sync import git_info

NAME = "git.exe" if sys.platform == "win32" else "git"


def _plant(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    f = directory / NAME
    f.write_text("x")
    f.chmod(0o755)
    return f


def _set_path(monkeypatch: pytest.MonkeyPatch, *dirs: object) -> None:
    monkeypatch.setenv("PATH", os.pathsep.join(str(d) for d in dirs))


def test_find_git_skips_root_and_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "repo"
    cwd = tmp_path / "cwd"
    good = tmp_path / "bin"
    _plant(root)
    _plant(root / "sub")
    _plant(cwd)
    planted = _plant(good)
    monkeypatch.chdir(cwd)
    _set_path(monkeypatch, "", ".", root, root / "sub", cwd, good)
    assert git_info.find_git(root) == str(planted.resolve())


def test_find_git_none_when_only_excluded(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "repo"
    _plant(root)
    monkeypatch.chdir(root)
    _set_path(monkeypatch, root, "")
    assert git_info.find_git(root) is None


def test_find_git_missing_and_empty_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _set_path(monkeypatch, tmp_path / "nope")
    assert git_info.find_git(tmp_path) is None
    monkeypatch.delenv("PATH")
    assert git_info.find_git(tmp_path) is None


def test_find_git_ignores_directory_named_git(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "bin" / NAME).mkdir(parents=True)
    _set_path(monkeypatch, tmp_path / "bin")
    assert git_info.find_git(tmp_path / "repo") is None


def test_git_env_drops_git_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GIT_DIR", "/evil")
    monkeypatch.setenv("git_work_tree", "/evil")
    monkeypatch.setenv("KEEP_ME", "1")
    env = git_info.git_env()
    assert "KEEP_ME" in env
    assert not any(k.upper().startswith("GIT_") for k in env)
    assert "GIT_DIR" in os.environ


class _Result:
    def __init__(self, code: int = 0, out: str = " out\n") -> None:
        self.returncode = code
        self.stdout = out


def _patch_run(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, **ret: Any) -> dict[str, Any]:
    seen: dict[str, Any] = {}
    monkeypatch.setattr(git_info, "find_git", lambda root: str(tmp_path / NAME))

    def fake(argv: Any, **kw: Any) -> _Result:
        seen["argv"] = argv
        seen["kw"] = kw
        if "raises" in ret:
            raise ret["raises"]
        return _Result(**{k: v for k, v in ret.items()})

    monkeypatch.setattr(subprocess, "run", fake)
    return seen


def test_run_git_call_shape(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GIT_DIR", "/evil")
    seen = _patch_run(monkeypatch, tmp_path)
    assert git_info.run_git(tmp_path, ["status"]) == "out"
    assert isinstance(seen["argv"], list)
    assert seen["argv"][1:] == ["-C", str(tmp_path), "status"]
    kw = seen["kw"]
    assert kw["shell"] is False
    assert kw["timeout"] == 10
    assert kw["stdin"] == subprocess.DEVNULL
    assert kw["stderr"] == subprocess.DEVNULL
    assert "GIT_DIR" not in kw["env"]


def test_run_git_nonzero(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_run(monkeypatch, tmp_path, code=1)
    assert git_info.run_git(tmp_path, ["x"]) is None


@pytest.mark.parametrize("exc", [subprocess.TimeoutExpired("git", 10), OSError("boom")])
def test_run_git_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, exc: Exception) -> None:
    _patch_run(monkeypatch, tmp_path, raises=exc)
    assert git_info.run_git(tmp_path, ["x"]) is None


def test_run_git_missing_git_runs_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(git_info, "find_git", lambda root: None)

    def boom(*a: Any, **k: Any) -> None:
        raise AssertionError("must not run")

    monkeypatch.setattr(subprocess, "run", boom)
    assert git_info.run_git(tmp_path, ["x"]) is None


def test_run_git_real_git_smoke(tmp_path: Path) -> None:
    if shutil.which("git") is None or git_info.find_git(tmp_path) is None:
        pytest.skip("git unavailable")
    assert git_info.run_git(tmp_path, ["--version"]).startswith("git version")  # type: ignore[union-attr]
