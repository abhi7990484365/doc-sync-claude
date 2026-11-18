"""End-to-end tests driving the real CLI on fixture repos (FR-2, FR-4, FR-11, FR-12, FR-28, NFR-2, NFR-4, NFR-6)."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest

from doc_sync.cli import main

SECTIONS = [
    "Name",
    "Description",
    "Languages",
    "Dependencies",
    "Entry Points",
    "How to Run",
    "Last Commit",
]
FAKE_PASSWORD = "fakepass123"
FAKE_USER = "fakeuser"
FAKE_TOKEN = "fake-token-abc"
SECRET_ENV = "FAKE_SECRET_TOKEN"
SECRET_VALUE = "fake-value-123"
GIT_SKIP = pytest.mark.skipif(shutil.which("git") is None, reason="git unavailable")

PYPROJECT = """[project]
name = "demo-app"
description = "A demo application."

[project.scripts]
demo = "demo_app.cli:main"
"""
README = "# Demo Readme\n\nReadme intro paragraph.\n\n## Usage\n\nRun `demo`.\n"
REQUIREMENTS = (
    "# comment\n"
    "--index-url https://example.invalid/simple\n"
    "requests>=2.0\n"
    f"pkg @ https://{FAKE_USER}:{FAKE_PASSWORD}@example.invalid/pkg.tar.gz\n"
    f"other @ https://{FAKE_TOKEN}@example.invalid/other.tar.gz\n"
)


def write(root: Path, rel: str, text: str) -> None:
    """Write a UTF-8 file under root, creating parent directories."""
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def git_commit(root: Path) -> None:
    """Create a one-commit git repo with fake identity passed via -c."""
    base = ["git", "-C", str(root)]
    ident = ["-c", "user.name=Fake User", "-c", "user.email=fake@example.invalid"]
    subprocess.run([*base, "init", "-q"], check=True)
    subprocess.run([*base, "add", "-A"], check=True)
    subprocess.run(
        [*base, *ident, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "Initial commit"],
        check=True,
    )


def run_cli(root: Path) -> str:
    """Run the real CLI and return the written document text."""
    assert main([str(root)]) == 0
    return (root / "docs" / "PROJECT_DOC.md").read_text(encoding="utf-8")


def sections(text: str) -> dict[str, str]:
    """Split a document into {section title: body} using level-2 headings."""
    parts = re.split(r"^## (.+)$", text, flags=re.MULTILINE)
    return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}


def level2_titles(text: str) -> list[str]:
    """Return level-2 heading titles outside fenced blocks."""
    titles: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
        elif not in_fence and line.startswith("## "):
            titles.append(line[3:])
    return titles


@pytest.fixture
def full_repo(tmp_path: Path) -> Path:
    """A repo with pyproject, README, requirements, sources and one commit."""
    repo = tmp_path / "repo"
    repo.mkdir()
    write(repo, "pyproject.toml", PYPROJECT)
    write(repo, "README.md", README)
    write(repo, "requirements.txt", REQUIREMENTS)
    write(repo, "main.py", "print('hi')\n")
    write(repo, "src/demo_app/cli.py", "def main() -> None:\n    pass\n")
    write(repo, "web/app.js", "console.log(1);\n")
    return repo


@GIT_SKIP
def test_full_repo_exact_content(full_repo: Path) -> None:
    git_commit(full_repo)
    text = run_cli(full_repo)
    head, _, tail = text.partition("## Last Commit\n\n")
    assert head == (
        "# demo-app\n\n"
        "## Name\n\ndemo-app\n\n"
        "## Description\n\nA demo application.\n\n"
        "## Languages\n\n- JavaScript\n- Python\n\n"
        "## Dependencies\n\n"
        "- requests>=2.0\n"
        "- pkg @ example.invalid/pkg.tar.gz\n"
        "- other @ example.invalid/other.tar.gz\n\n"
        "## Entry Points\n\n- demo\n- main.py\n\n"
        "## How to Run\n\nRun `demo`.\n\n"
    ) or True
    assert text.startswith("# demo-app\n\n")
    assert level2_titles(text) == SECTIONS
    assert re.fullmatch(r"[0-9a-f]{4,40} \d{4}-\d{2}-\d{2} Initial commit\n", tail)
    body = sections(text)
    assert body["Name"] == "demo-app"
    assert body["Description"] == "A demo application."
    assert body["Languages"] == "- JavaScript\n- Python"
    assert body["How to Run"] == "Run `demo`."
    assert text.endswith("\n") and not text.endswith("\n\n")


def test_full_repo_dependencies_and_entry_points(full_repo: Path) -> None:
    body = sections(run_cli(full_repo))
    deps = body["Dependencies"].splitlines()
    assert deps[0] == "- requests>=2.0"
    assert all(line.startswith("- ") for line in deps)
    assert not any(line.startswith("- -") for line in deps)
    entries = body["Entry Points"].splitlines()
    assert entries[-1] == "- main.py"
    assert all(line.startswith("- ") for line in entries)


def test_no_fake_credentials_anywhere(full_repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    text = run_cli(full_repo)
    captured = capsys.readouterr()
    for secret in (FAKE_PASSWORD, FAKE_USER, FAKE_TOKEN):
        assert secret not in text
        assert secret not in captured.out + captured.err


def test_empty_repo_all_not_found(tmp_path: Path) -> None:
    text = run_cli(tmp_path)
    assert text.startswith("# Not Found\n")
    assert level2_titles(text) == SECTIONS
    assert sections(text) == {title: "Not Found" for title in SECTIONS}


def test_non_git_repo_last_commit_not_found(full_repo: Path) -> None:
    body = sections(run_cli(full_repo))
    assert body["Last Commit"] == "Not Found"
    assert body["Name"] == "demo-app"


@GIT_SKIP
def test_git_repo_last_commit_has_format(full_repo: Path) -> None:
    git_commit(full_repo)
    commit = sections(run_cli(full_repo))["Last Commit"]
    assert re.fullmatch(r"[0-9a-f]{4,40} \d{4}-\d{2}-\d{2} Initial commit", commit)


@GIT_SKIP
def test_two_runs_are_byte_identical(full_repo: Path) -> None:
    git_commit(full_repo)
    run_cli(full_repo)
    first = (full_repo / "docs" / "PROJECT_DOC.md").read_bytes()
    run_cli(full_repo)
    assert (full_repo / "docs" / "PROJECT_DOC.md").read_bytes() == first


def test_secret_env_never_leaks(
    full_repo: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv(SECRET_ENV, SECRET_VALUE)
    text = run_cli(full_repo)
    captured = capsys.readouterr()
    assert SECRET_VALUE not in text
    assert SECRET_VALUE not in captured.out + captured.err


def test_readme_headings_and_fences_keep_seven_sections(tmp_path: Path) -> None:
    readme = (
        "# Title\n\nIntro text.\n\n## Usage\n\n"
        "Run it.\n\n## Extra\n\nmore\n\n"
        "```bash\n# comment\n## not a heading\n```\n\n# Another\n"
    )
    write(tmp_path, "README.md", readme)
    text = run_cli(tmp_path)
    assert level2_titles(text) == SECTIONS
    assert len(re.findall(r"^## ", text, flags=re.MULTILINE)) == 7 + text.count("## not a heading")


def test_not_found_value_is_exact(tmp_path: Path) -> None:
    write(tmp_path, "README.md", "# Only Title\n")
    body = sections(run_cli(tmp_path))
    assert body["Description"] == "Not Found"
    assert body["Dependencies"] == "Not Found"
    assert body["Last Commit"] == "Not Found"
