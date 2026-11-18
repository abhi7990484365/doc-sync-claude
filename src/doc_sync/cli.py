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
    args.empty_path = args.repo_path == ""
    args.repo_path = Path(args.repo_path) if args.repo_path is not None else Path.cwd()
    return args


def resolve_repo(path: Path) -> Path | None:
    """Return the path when it is a directory, else None."""
    return path if Path(path).is_dir() else None


def path_error(path: Path) -> str:
    """Return the one-line error message for an invalid REPO_PATH."""
    if Path(path).exists():
        return "REPO_PATH is not a directory"
    return f"REPO_PATH not found: {path}"


def safe_line(text: str) -> str:
    """Return text that the stdout encoding can represent (backslash escapes)."""
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    return text.encode(encoding, errors="backslashreplace").decode(encoding)


def write_failure(exc: OSError) -> str:
    """Return the one-line message for a failed write."""
    return f"Could not write document: {exc.strerror or type(exc).__name__}"


def main(argv: Sequence[str] | None = None) -> int:
    """Run the tool and return the process exit code."""
    try:
        args = parse_args(argv)
    except OSError:
        print("Could not determine the current directory", file=sys.stderr)
        return EXIT_USAGE
    root = None if args.empty_path else resolve_repo(args.repo_path)
    if root is None:
        message = "REPO_PATH not found: " if args.empty_path else path_error(args.repo_path)
        print(safe_line(message), file=sys.stderr)
        return EXIT_USAGE
    text = render_document(collect(root))
    try:
        target = write_doc(root, text)
    except OSError as exc:
        print(safe_line(write_failure(exc)), file=sys.stderr)
        return EXIT_WRITE_ERROR
    print(safe_line(f"Wrote {target}"))
    return EXIT_OK
