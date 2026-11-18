"""Map file extensions to language names."""

from __future__ import annotations

from pathlib import Path

_LANGUAGE_EXTENSIONS: dict[str, tuple[str, ...]] = {
    "C": (".c", ".h"),
    "C#": (".cs",),
    "C++": (".cpp", ".cc", ".cxx", ".hpp", ".hh"),
    "CSS": (".css",),
    "Go": (".go",),
    "HTML": (".html", ".htm"),
    "Java": (".java",),
    "JavaScript": (".js", ".mjs", ".cjs", ".jsx"),
    "Kotlin": (".kt", ".kts"),
    "PHP": (".php",),
    "PowerShell": (".ps1", ".psm1"),
    "Python": (".py", ".pyi"),
    "Ruby": (".rb",),
    "Rust": (".rs",),
    "Scala": (".scala",),
    "Shell": (".sh", ".bash"),
    "SQL": (".sql",),
    "Swift": (".swift",),
    "TypeScript": (".ts", ".tsx"),
}

EXTENSION_LANGUAGES: dict[str, str] = {
    ext: language
    for language, extensions in _LANGUAGE_EXTENSIONS.items()
    for ext in extensions
}


def detect_languages(files: list[Path]) -> list[str]:
    """Return unique language names for the files, sorted alphabetically."""
    found = {
        EXTENSION_LANGUAGES[suffix]
        for suffix in (path.suffix.lower() for path in files)
        if suffix in EXTENSION_LANGUAGES
    }
    return sorted(found)
