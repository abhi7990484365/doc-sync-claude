"""TASK-019: create-user (FR-12, AC-11, N-17)."""

import secrets
from pathlib import Path

import pytest
from sqlalchemy import select

from employee_app.db.engine import session_scope
from employee_app.db.models import User
from employee_app.db.users import find_user_by_username
from employee_app.security import verify_password
from tests.cmd_helpers import cmd_env, create_user_input, run_cli
from tests.conftest import make_engine


@pytest.fixture
def env(db_file: Path) -> dict[str, str]:
    environment = cmd_env(db_file)
    assert run_cli(["init-db"], environment).exit_code == 0
    return environment


def stored(db_file: Path, username: str):  # type: ignore[no-untyped-def]
    return find_user_by_username(make_engine(db_file), username.casefold())


def test_creates_user_with_hashed_password_role_and_version(env, db_file) -> None:
    secret = secrets.token_urlsafe(18)
    result = run_cli(["create-user"], env, create_user_input("  Admin One ", secret))
    assert result.exit_code == 0, result.output
    user = stored(db_file, "admin one")
    assert user is not None
    assert user.role == "hr_administrator" and user.auth_version == 0 and user.is_active
    assert user.password_hash != secret and secret not in user.password_hash
    assert verify_password(user.password_hash, secret)


def test_output_never_contains_the_password(env) -> None:
    secret = secrets.token_urlsafe(18)
    result = run_cli(["create-user"], env, create_user_input("a1", secret))
    assert secret not in result.output


def test_password_environment_variable_is_ignored(env, db_file) -> None:
    from_env = secrets.token_urlsafe(18)
    typed = secrets.token_urlsafe(18)
    environment = env | {"EMPLOYEE_APP_PASSWORD": from_env, "PASSWORD": from_env}
    assert run_cli(["create-user"], environment, create_user_input("a1", typed)).exit_code == 0
    user = stored(db_file, "a1")
    assert verify_password(user.password_hash, typed)
    assert not verify_password(user.password_hash, from_env)


@pytest.mark.parametrize("password", ["", "x" * 11])
def test_weak_or_empty_password_rejected(env, db_file, password: str) -> None:
    result = run_cli(["create-user"], env, create_user_input("a1", password))
    assert result.exit_code != 0
    assert stored(db_file, "a1") is None
    assert "Password rejected" in result.output


def test_mismatched_confirmation_rejected(env, db_file) -> None:
    result = run_cli(["create-user"], env, create_user_input("a1", "x" * 14, "y" * 14) + "\n\n\n")
    assert result.exit_code != 0
    assert stored(db_file, "a1") is None


def test_duplicate_username_including_case_only_rejected(env, db_file) -> None:
    secret = secrets.token_urlsafe(18)
    assert run_cli(["create-user"], env, create_user_input("Admin", secret)).exit_code == 0
    result = run_cli(["create-user"], env, create_user_input("ADMIN", secret))
    assert result.exit_code != 0 and "already exists" in result.output
    with session_scope(make_engine(db_file)) as s:
        assert len(s.scalars(select(User)).all()) == 1


def test_empty_and_overlong_usernames_rejected(env) -> None:
    secret = secrets.token_urlsafe(18)
    assert run_cli(["create-user"], env, create_user_input("   ", secret)).exit_code != 0
    assert run_cli(["create-user"], env, create_user_input("u" * 101, secret)).exit_code != 0
    assert run_cli(["create-user"], env, create_user_input("u" * 100, secret)).exit_code == 0


def test_password_is_not_accepted_as_an_option(env) -> None:
    result = run_cli(["create-user", "--password", "x"], env, "a\n")
    assert result.exit_code != 0 and "No such option" in result.output
