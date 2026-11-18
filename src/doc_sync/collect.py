"""Build the ProjectInfo data model (FR-5, FR-11..FR-16). Missing data is None/[]."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from doc_sync.dependencies import read_dependencies
from doc_sync.entry_points import collect_entry_points
from doc_sync.fs import is_dir, iter_repo_files
from doc_sync.git_info import last_commit
from doc_sync.languages import detect_languages
from doc_sync.pyproject import load_pyproject, project_field
from doc_sync.readme import first_heading, first_paragraph, load_readme, section_body

HOW_TO_RUN_TITLES: tuple[str, ...] = ("Usage", "How to Run")


@dataclass(frozen=True)
class ProjectInfo:
    """Facts about a repository. None / [] mean the data is missing."""

    name: str | None = None
    description: str | None = None
    languages: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    entry_points: list[str] = field(default_factory=list)
    how_to_run: str | None = None
    last_commit: str | None = None


def first_present(*values: str | None) -> str | None:
    """Return the first value that is a non-blank string, else None."""
    for value in values:
        if isinstance(value, str) and value.strip():
            return value
    return None


def _readme_field(readme: str | None, parser: Callable[[str], str | None]) -> str | None:
    """Apply a README parser, returning None when there is no README."""
    return None if readme is None else parser(readme)


def collect(root: Path) -> ProjectInfo:
    """Collect all project facts under root. Never raises."""
    root = Path(root)
    if not is_dir(root):
        return ProjectInfo()
    data = load_pyproject(root)
    readme = load_readme(root)
    files = iter_repo_files(root)
    return ProjectInfo(
        name=first_present(
            project_field(data, "name"), _readme_field(readme, first_heading)
        ),
        description=first_present(
            project_field(data, "description"),
            _readme_field(readme, first_paragraph),
        ),
        languages=detect_languages(files),
        dependencies=read_dependencies(root),
        entry_points=collect_entry_points(root, data, files),
        how_to_run=_readme_field(
            readme, lambda text: section_body(text, HOW_TO_RUN_TITLES)
        ),
        last_commit=last_commit(root),
    )
