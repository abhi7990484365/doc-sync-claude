"""Safe git invocation: own PATH walk, sanitised env, single subprocess site."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

GIT_TIMEOUT_SECONDS = 10
COMMIT_PATTERN = re.compile(r"[0-9a-f]{4,40} \d{4}-\d{2}-\d{2} \S.*")
LOG_ARGS = ["log", "-1", "--no-show-signature", "--no-color", "--format=%h %ad %s", "--date=short"]


def _git_name() -> str:
    """Return the git executable file name for this platform."""
    return "git.exe" if sys.platform == "win32" else "git"


def _resolve(path: Path) -> Path | None:
    """Resolve a path to an absolute path, or None on OSError/ValueError."""
    try:
        return path.resolve()
    except (OSError, ValueError, RuntimeError):
        return None


def _is_inside(path: Path, parent: Path) -> bool:
    """Return True if path equals parent or is inside it."""
    return path == parent or parent in path.parents


def _is_executable_file(path: Path) -> bool:
    """Return True for a regular file that can be executed."""
    try:
        if not path.is_file():
            return False
    except OSError:
        return False
    return sys.platform == "win32" or os.access(path, os.X_OK)


def _is_excluded_dir(directory: Path, cwd: Path, root: Path) -> bool:
    """Return True if the dir is the cwd or is/inside the repo root."""
    return _is_inside(directory, cwd) or _is_inside(directory, root)


def find_git(root: Path) -> str | None:
    """Find an absolute git path on PATH, excluding the cwd and repo root."""
    resolved_root = _resolve(Path(root))
    cwd = _resolve(Path.cwd())
    if resolved_root is None or cwd is None:
        return None
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if entry.strip() in ("", ".") or not Path(entry).is_absolute():
            continue
        directory = _resolve(Path(entry))
        if directory is None or _is_excluded_dir(directory, cwd, resolved_root):
            continue
        candidate = directory / _git_name()
        if _is_executable_file(candidate):
            return str(candidate)
    return None


def git_env() -> dict[str, str]:
    """Return a copy of os.environ without any `GIT_*` variables."""
    return {k: v for k, v in os.environ.items() if not k.upper().startswith("GIT_")}


def run_git(root: Path, args: list[str]) -> str | None:
    """Run git in root; return stripped stdout, or None on any failure."""
    git = find_git(root)
    if git is None:
        return None
    try:
        result = subprocess.run(
            [git, "-C", str(root), *args],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdin=subprocess.DEVNULL,
            timeout=GIT_TIMEOUT_SECONDS,
            check=False,
            env=git_env(),
        )
    except (subprocess.TimeoutExpired, OSError, ValueError):
        return None
    if result.returncode != 0:
        return None
    return (result.stdout or "").strip()


def is_top_level(root: Path) -> bool:
    """Return True only if root is the top-level directory of a git work tree."""
    top = run_git(root, ["rev-parse", "--show-toplevel"])
    if not top or "\n" in top:
        return False
    resolved_top = _resolve(Path(top))
    resolved_root = _resolve(Path(root))
    if resolved_top is None or resolved_root is None:
        return False
    return os.path.normcase(str(resolved_top)) == os.path.normcase(str(resolved_root))


def last_commit(root: Path) -> str | None:
    """Return `<hash> <date> <subject>` of HEAD for a top-level repo, else None."""
    if not is_top_level(root):
        return None
    out = run_git(root, LOG_ARGS)
    if out is None or len(out.splitlines()) != 1 or not COMMIT_PATTERN.fullmatch(out):
        return None
    return out
