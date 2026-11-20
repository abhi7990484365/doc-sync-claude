"""TASK-021: unlock-user (FR-18; AC-16, AC-17, P-14, P-15, E-18)."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from employee_app.config import LockoutSettings
from employee_app.db.lockout import record_failure
from employee_app.db.users import find_user_by_username
from tests.cmd_helpers import cmd_env, run_cli
from tests.conftest import add_user

NOW = datetime(2026, 11, 20, 12, 0, tzinfo=timezone.utc)


@pytest.fixture
def env(db_file: Path, engine) -> dict[str, str]:
    return cmd_env(db_file)


def lock(engine, uid: int) -> None:  # type: ignore[no-untyped-def]
    for _ in range(5):
        record_failure(engine, uid, NOW, LockoutSettings())


def test_unlock_clears_count_and_lock_of_a_locked_account(env, engine) -> None:  # AC-16 part
    uid = add_user(engine, "Admin1")
    lock(engine, uid)
    assert find_user_by_username(engine, "admin1").locked_until == NOW + timedelta(minutes=15)
    result = run_cli(["unlock-user", "admin1"], env)
    assert result.exit_code == 0, result.output
    user = find_user_by_username(engine, "admin1")
    assert (user.failed_login_count, user.locked_until) == (0, None)


def test_second_run_gives_the_same_result(env, engine) -> None:  # P-15 idempotent
    uid = add_user(engine, "admin1")
    lock(engine, uid)
    assert run_cli(["unlock-user", "admin1"], env).exit_code == 0
    first = find_user_by_username(engine, "admin1")
    assert run_cli(["unlock-user", "admin1"], env).exit_code == 0
    assert find_user_by_username(engine, "admin1") == first


def test_unlocked_account_is_unchanged_including_flags_hash_and_version(env, engine) -> None:  # AC-17
    add_user(engine, "admin1")
    before = find_user_by_username(engine, "admin1")
    assert run_cli(["unlock-user", "admin1"], env).exit_code == 0
    assert find_user_by_username(engine, "admin1") == before


def test_unlock_does_not_change_is_active_password_or_auth_version(env, engine) -> None:  # AC-17
    uid = add_user(engine, "admin1")
    lock(engine, uid)
    before = find_user_by_username(engine, "admin1")
    run_cli(["unlock-user", "admin1"], env)
    after = find_user_by_username(engine, "admin1")
    assert (after.is_active, after.password_hash, after.auth_version) == (
        before.is_active, before.password_hash, before.auth_version)


def test_unknown_username_exits_non_zero_and_changes_no_row(env, engine) -> None:  # E-18 approved Proposal
    uid = add_user(engine, "admin1")
    lock(engine, uid)
    before = find_user_by_username(engine, "admin1")
    result = run_cli(["unlock-user", "nobody"], env)
    assert result.exit_code != 0 and "Unknown username" in result.output
    assert find_user_by_username(engine, "admin1") == before


def test_output_has_no_password_or_hash(env, engine) -> None:
    add_user(engine, "admin1")
    stored_hash = find_user_by_username(engine, "admin1").password_hash
    assert stored_hash not in run_cli(["unlock-user", "admin1"], env).output
