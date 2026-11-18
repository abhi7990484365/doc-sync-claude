"""Atomic writing of the generated document."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

DOCS_DIR = "docs"
OUTPUT_NAME = "PROJECT_DOC.md"


def atomic_write(path: Path, text: str) -> None:
    """Write text to path via a temp file in the same directory and os.replace."""
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=".doc-sync-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", errors="replace", newline="\n") as handle:
            handle.write(text)
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def write_doc(root: Path, text: str) -> Path:
    """Write text to <root>/docs/PROJECT_DOC.md and return that path."""
    docs = Path(root) / DOCS_DIR
    docs.mkdir(parents=True, exist_ok=True)
    target = docs / OUTPUT_NAME
    atomic_write(target, text)
    return target
