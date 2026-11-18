"""Command-line entry point for doc_sync."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from doc_sync.collect import collect
from doc_sync.render import render_document
from doc_sync.writer import write_doc

EXIT_OK = 0
EXIT_WRITE_ERROR = 1
EXIT_USAGE = 2


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse arguments; REPO_PATH is optional and defaults to the cwd."""
    parser = argparse.ArgumentParser(
        prog="doc_sync", description="Write docs/PROJECT_DOC.md for a repository."
    )
    parser.add_argument("repo_path", metavar="REPO_PATH", nargs="?", default=None)
    args = parser.parse_args(argv)
    args.repo_path = Path(args.repo_path) if args.repo_path else Path.cwd()
    return args


def resolve_repo(path: Path) -> Path | None:
    """Return the path when it is a directory, else None."""
    return path if Path(path).is_dir() else None


def path_error(path: Path) -> str:
    """Return the one-line error message for an invalid REPO_PATH."""
    if Path(path).exists():
        return "REPO_PATH is not a directory"
    return f"REPO_PATH not found: {path}"


def main(argv: Sequence[str] | None = None) -> int:
    """Run the tool and return the process exit code."""
    args = parse_args(argv)
    root = resolve_repo(args.repo_path)
    if root is None:
        print(path_error(args.repo_path), file=sys.stderr)
        return EXIT_USAGE
    try:
        target = write_doc(root, render_document(collect(root)))
    except OSError as exc:
        reason = exc.strerror or type(exc).__name__
        print(f"Could not write document: {reason}", file=sys.stderr)
        return EXIT_WRITE_ERROR
    print(f"Wrote {target}")
    return EXIT_OK
