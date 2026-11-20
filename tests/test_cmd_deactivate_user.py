"""TASK-020: deactivate-user (FR-12, AC-12)."""

from pathlib import Path

import pytest

from employee_app.db.users import find_user_by_username
from tests.cmd_helpers import cmd_env, run_cli
from tests.conftest import add_user, make_engine


@pytest.fixture
def env(db_file: Path, engine) -> dict[str, str]:  # engine fixture creates the schema
    return cmd_env(db_file)


def test_deactivation_sets_flag_and_bumps_auth_version(env, engine) -> None:
    add_user(engine, "Admin1")
    result = run_cli(["deactivate-user", "ADMIN1"], env)
    assert result.exit_code == 0, result.output
    user = find_user_by_username(engine, "admin1")
    assert user.is_active is False and user.auth_version == 1


def test_repeat_run_is_safe(env, engine) -> None:
    add_user(engine, "admin1")
    assert run_cli(["deactivate-user", "admin1"], env).exit_code == 0
    assert run_cli(["deactivate-user", "admin1"], env).exit_code == 0
    assert find_user_by_username(engine, "admin1").is_active is False


def test_unknown_username_errors_and_changes_nothing(env, engine) -> None:
    uid = add_user(engine, "admin1")
    result = run_cli(["deactivate-user", "nobody"], env)
    assert result.exit_code != 0 and "Unknown username" in result.output
    assert find_user_by_username(engine, "admin1").id == uid
    assert find_user_by_username(engine, "admin1").is_active is True


def test_output_has_no_password_or_hash(env, engine) -> None:
    add_user(engine, "admin1")
    stored_hash = find_user_by_username(engine, "admin1").password_hash
    result = run_cli(["deactivate-user", "admin1"], env)
    assert stored_hash not in result.output
