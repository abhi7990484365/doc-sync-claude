"""Tests for git_info: find_git, git_env, run_git."""

from __future__ import annotations

import os
import re
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


def test_find_git_skips_relative_and_inside_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cwd = tmp_path / "cwd"
    _plant(cwd / "bin")
    _plant(cwd / "rel")
    other = tmp_path / "other"
    monkeypatch.chdir(cwd)
    _set_path(monkeypatch, "rel", os.path.join("..", "cwd", "rel"), cwd / "bin")
    assert git_info.find_git(other) is None
    good = _plant(tmp_path / "good")
    _set_path(monkeypatch, "rel", cwd / "bin", good.parent)
    assert git_info.find_git(other) == str(good.resolve())


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


GOOD = "abc1234 2024-05-06 fix: thing"


def _fake_git(monkeypatch: pytest.MonkeyPatch, top: str | None, log: str | None) -> None:
    def fake(root: Path, args: list[str]) -> str | None:
        return top if args[0] == "rev-parse" else log

    monkeypatch.setattr(git_info, "run_git", fake)


def test_last_commit_accepts_good(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_git(monkeypatch, str(tmp_path), GOOD)
    assert git_info.last_commit(tmp_path) == GOOD


@pytest.mark.parametrize(
    "bad",
    [
        "gpg: Good signature\n" + GOOD,
        "\x1b[33mabc1234\x1b[m 2024-05-06 x",
        GOOD + "\nsecond line",
        *[GOOD + sep + "x" for sep in ("\x0b", "\x0c", "\x1c", "\x1d", "\x1e", "\x85", " ", " ")],
        "",
        None,
        "abc 2024-05-06 x",
        "abc1234 2024-05-06 ",
    ],
)
def test_last_commit_rejects_bad(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, bad: str | None) -> None:
    _fake_git(monkeypatch, str(tmp_path), bad)
    assert git_info.last_commit(tmp_path) is None


def test_last_commit_none_when_not_top_level(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _fake_git(monkeypatch, str(tmp_path.parent), GOOD)
    assert git_info.is_top_level(tmp_path) is False
    assert git_info.last_commit(tmp_path) is None


@pytest.mark.parametrize("top", [None, "", "a\nb"])
def test_is_top_level_failures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, top: str | None) -> None:
    _fake_git(monkeypatch, top, GOOD)
    assert git_info.is_top_level(tmp_path) is False


def _git_or_skip(path: Path) -> None:
    if shutil.which("git") is None or git_info.find_git(path) is None:
        pytest.skip("git unavailable")


def _real(path: Path, *args: str) -> None:
    git = git_info.find_git(path)
    assert git is not None
    cfg = ["-c", "user.name=Test", "-c", "user.email=test@example.invalid", "-c", "commit.gpgsign=false"]
    subprocess.run([git, "-C", str(path), *cfg, *args], check=True, env=git_info.git_env(),
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def test_real_repo_with_commit(tmp_path: Path) -> None:
    _git_or_skip(tmp_path)
    _real(tmp_path, "init")
    (tmp_path / "a.txt").write_text("a")
    _real(tmp_path, "add", "a.txt")
    _real(tmp_path, "commit", "-m", "first commit")
    assert git_info.is_top_level(tmp_path) is True
    out = git_info.last_commit(tmp_path)
    assert out is not None
    assert re.fullmatch(r"[0-9a-f]{4,40} \d{4}-\d{2}-\d{2} first commit", out)


def test_real_repo_no_commits(tmp_path: Path) -> None:
    _git_or_skip(tmp_path)
    _real(tmp_path, "init")
    assert git_info.last_commit(tmp_path) is None


def test_real_subfolder_of_repo(tmp_path: Path) -> None:
    _git_or_skip(tmp_path)
    _real(tmp_path, "init")
    sub = tmp_path / "sub"
    sub.mkdir()
    assert git_info.is_top_level(sub) is False
    assert git_info.last_commit(sub) is None


def test_real_not_a_repo(tmp_path: Path) -> None:
    _git_or_skip(tmp_path)
    assert git_info.last_commit(tmp_path) is None
