"""TASK-043 (NR-15): operator action logging carries command name and id only."""

import logging
import secrets
from pathlib import Path

import pytest

from employee_app.db.users import find_user_by_username
from tests.cmd_helpers import cmd_env, create_user_input, run_cli
from tests.conftest import add_user

USERNAME = "secretlooking-name"


@pytest.fixture
def env(db_file: Path, engine) -> dict[str, str]:
    return cmd_env(db_file)


def operator_lines(caplog: pytest.LogCaptureFixture) -> list[str]:
    return [r.getMessage() for r in caplog.records if r.name == "employee_app"]


def test_create_user_success_logs_command_and_id_only(env, engine, caplog) -> None:
    secret = secrets.token_urlsafe(18)
    with caplog.at_level(logging.INFO, logger="employee_app"):
        assert run_cli(["create-user"], env, create_user_input(USERNAME, secret)).exit_code == 0
    uid = find_user_by_username(engine, USERNAME).id
    assert operator_lines(caplog) == [f"operator_command command=create-user outcome=created user_id={uid}"]


def test_weak_password_logs_no_username_or_password(env, caplog) -> None:
    weak = "short-" + secrets.token_hex(2)
    with caplog.at_level(logging.INFO, logger="employee_app"):
        run_cli(["create-user"], env, create_user_input(USERNAME, weak))
    text = " ".join(operator_lines(caplog))
    assert "command=create-user outcome=rejected" in text
    assert USERNAME not in text and weak not in text


@pytest.mark.parametrize("command", ["unlock-user", "deactivate-user"])
def test_unknown_username_line_has_no_username_or_id(env, caplog, command: str) -> None:
    with caplog.at_level(logging.INFO, logger="employee_app"):
        run_cli([command, USERNAME], env)
    assert operator_lines(caplog) == [f"operator_command command={command} outcome=unknown_user"]


@pytest.mark.parametrize("command", ["unlock-user", "deactivate-user"])
def test_success_line_has_command_and_user_id(env, engine, caplog, command: str) -> None:
    uid = add_user(engine, USERNAME)
    with caplog.at_level(logging.INFO, logger="employee_app"):
        run_cli([command, USERNAME], env)
    assert operator_lines(caplog) == [f"operator_command command={command} outcome=ok user_id={uid}"]


def test_duplicate_username_logs_no_username(env, engine, caplog) -> None:
    add_user(engine, USERNAME)
    with caplog.at_level(logging.INFO, logger="employee_app"):
        run_cli(["create-user"], env, create_user_input(USERNAME, secrets.token_urlsafe(18)))
    text = " ".join(operator_lines(caplog))
    assert "outcome=duplicate" in text and USERNAME not in text


def test_init_db_logs_ok(env, caplog) -> None:
    with caplog.at_level(logging.INFO, logger="employee_app"):
        run_cli(["init-db"], env)
    assert operator_lines(caplog) == ["operator_command command=init-db outcome=ok"]
