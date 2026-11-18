from pathlib import Path

import pytest

from doc_sync.dependencies import (
    clean_requirement,
    parse_requirements,
    read_dependencies,
    strip_url_credentials,
)


def test_parse_basic_order() -> None:
    assert parse_requirements("requests>=2\nflake8\n") == ["requests>=2", "flake8"]


def test_blank_and_comment_lines_skipped() -> None:
    assert parse_requirements("\n   \n# note\n  # indented\nA\n") == ["A"]


@pytest.mark.parametrize(
    "line",
    [
        "-r other.txt",
        "-e .",
        "--index-url https://user:fakepass@host/simple",
        "--extra-index-url https://fake-token@host/simple",
    ],
)
def test_option_lines_skipped(line: str) -> None:
    assert clean_requirement(line) is None
    assert parse_requirements(line) == []


def test_inline_comment_stripped() -> None:
    assert clean_requirement("pkg==1.0  # pinned") == "pkg==1.0"
    assert clean_requirement("pkg # c") == "pkg"


def test_hash_without_space_kept() -> None:
    assert clean_requirement("pkg @ https://h/x#egg=pkg") == "pkg @ https://h/x#egg=pkg"


def test_user_pass_removed() -> None:
    out = strip_url_credentials("https://user:fakepass@host/p")
    assert out == "https://host/p"


def test_token_removed_from_direct_reference() -> None:
    out = clean_requirement("pkg @ https://faketoken@github.com/x/y.git")
    assert out == "pkg @ https://github.com/x/y.git"


def test_credentials_never_reach_output() -> None:
    text = (
        "--index-url https://user:fakepass@host/simple\n"
        "a @ https://user:fakepass@host/a.whl\n"
        "b @ git+https://faketoken@github.com/x/b.git  # faketoken\n"
        "c @ https://us@er:fakepass@host/c\n"
    )
    joined = "\n".join(parse_requirements(text))
    assert "fakepass" not in joined
    assert "faketoken" not in joined
    assert "user:" not in joined
    assert "@host" not in joined
    assert "@github" not in joined


def test_no_url_unchanged() -> None:
    assert strip_url_credentials("pkg==1 ; python_version>'3'") == "pkg==1 ; python_version>'3'"


def test_read_dependencies_file(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("a\n# c\nb\n", encoding="utf-8")
    assert read_dependencies(tmp_path) == ["a", "b"]


def test_read_dependencies_missing_and_empty(tmp_path: Path) -> None:
    assert read_dependencies(tmp_path) == []
    (tmp_path / "requirements.txt").write_text("", encoding="utf-8")
    assert read_dependencies(tmp_path) == []


def test_read_dependencies_unreadable(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_bytes(b"\xff\xfe\x00bad\xff")
    assert read_dependencies(tmp_path) == []
    (tmp_path / "requirements.txt").unlink()
    (tmp_path / "requirements.txt").mkdir()
    assert read_dependencies(tmp_path) == []
