"""FR-15/FR-16: pyproject wins; each field falls back independently."""

from pathlib import Path

from doc_sync.collect import collect, first_present

README = "# Readme Name\n\nReadme description.\n"


def _write(root: Path, name: str, text: str) -> None:
    (root / name).write_text(text, encoding="utf-8")


def test_first_present_skips_none_and_blank() -> None:
    assert first_present(None, "  ", "x", "y") == "x"
    assert first_present(None, "") is None
    assert first_present() is None


def test_pyproject_wins(tmp_path: Path) -> None:
    _write(tmp_path, "pyproject.toml", '[project]\nname = "pp"\ndescription = "pd"\n')
    _write(tmp_path, "README.md", README)
    info = collect(tmp_path)
    assert (info.name, info.description) == ("pp", "pd")


def test_name_from_pyproject_description_from_readme(tmp_path: Path) -> None:
    _write(tmp_path, "pyproject.toml", '[project]\nname = "pp"\n')
    _write(tmp_path, "README.md", README)
    info = collect(tmp_path)
    assert (info.name, info.description) == ("pp", "Readme description.")


def test_description_from_pyproject_name_from_readme(tmp_path: Path) -> None:
    _write(tmp_path, "pyproject.toml", '[project]\ndescription = "pd"\n')
    _write(tmp_path, "README.md", README)
    info = collect(tmp_path)
    assert (info.name, info.description) == ("Readme Name", "pd")


def test_blank_pyproject_values_fall_back(tmp_path: Path) -> None:
    _write(tmp_path, "pyproject.toml", '[project]\nname = "  "\ndescription = 5\n')
    _write(tmp_path, "README.md", README)
    info = collect(tmp_path)
    assert (info.name, info.description) == ("Readme Name", "Readme description.")
