from __future__ import annotations

from pathlib import Path

import pytest

from doc_sync.languages import EXTENSION_LANGUAGES, detect_languages

EXPECTED = {
    ".c": "C", ".h": "C", ".cs": "C#",
    ".cpp": "C++", ".cc": "C++", ".cxx": "C++", ".hpp": "C++", ".hh": "C++",
    ".css": "CSS", ".go": "Go", ".html": "HTML", ".htm": "HTML",
    ".java": "Java",
    ".js": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript",
    ".jsx": "JavaScript",
    ".kt": "Kotlin", ".kts": "Kotlin", ".php": "PHP",
    ".ps1": "PowerShell", ".psm1": "PowerShell",
    ".py": "Python", ".pyi": "Python", ".rb": "Ruby", ".rs": "Rust",
    ".scala": "Scala", ".sh": "Shell", ".bash": "Shell", ".sql": "SQL",
    ".swift": "Swift", ".ts": "TypeScript", ".tsx": "TypeScript",
}


def test_table_matches_architecture() -> None:
    assert EXTENSION_LANGUAGES == EXPECTED
    assert len(set(EXPECTED.values())) == 19


@pytest.mark.parametrize(("ext", "language"), sorted(EXPECTED.items()))
def test_each_extension_maps(ext: str, language: str) -> None:
    assert detect_languages([Path(f"x{ext}")]) == [language]


def test_case_insensitive_suffix() -> None:
    assert detect_languages([Path("A.PY"), Path("b.Rs")]) == ["Python", "Rust"]


def test_unique() -> None:
    assert detect_languages([Path("a.py"), Path("b.pyi"), Path("c.py")]) == ["Python"]


def test_sorted_alphabetically() -> None:
    files = [Path("a.ts"), Path("b.go"), Path("c.py"), Path("d.c")]
    assert detect_languages(files) == ["C", "Go", "Python", "TypeScript"]


def test_unknown_ignored() -> None:
    assert detect_languages([Path("a.md"), Path("b.json"), Path("c.xyz")]) == []


def test_no_extension_ignored() -> None:
    assert detect_languages([Path("Makefile"), Path("LICENSE"), Path(".gitignore")]) == []


def test_empty_input() -> None:
    assert detect_languages([]) == []
