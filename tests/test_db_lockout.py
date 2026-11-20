"""TASK-016: lockout, unlock and auth_version conditional updates."""

from datetime import datetime, timedelta, timezone

from employee_app.config import LockoutSettings
from employee_app.db.lockout import record_failure, record_success, unlock
from employee_app.db.users import deactivate_user_by_id, get_user, increment_auth_version
from tests.conftest import add_user, make_engine

NOW = datetime(2026, 11, 20, 12, 0, tzinfo=timezone.utc)
SETTINGS = LockoutSettings(max_failures=5, lock_minutes=15)


def fail_times(engine, user_id: int, times: int, now: datetime = NOW) -> None:  # type: ignore[no-untyped-def]
    for _ in range(times):
        record_failure(engine, user_id, now, SETTINGS)


def test_fifth_failure_sets_the_lock(engine) -> None:
    uid = add_user(engine)
    fail_times(engine, uid, 4)
    view = get_user(engine, uid)
    assert view.failed_login_count == 4 and view.locked_until is None
    assert record_failure(engine, uid, NOW, SETTINGS) is True
    view = get_user(engine, uid)
    assert view.failed_login_count == 5
    assert view.locked_until == NOW + timedelta(minutes=15)
    assert view.is_locked(NOW)


def test_no_change_while_locked(engine) -> None:
    uid = add_user(engine)
    fail_times(engine, uid, 5)
    before = get_user(engine, uid)
    assert record_failure(engine, uid, NOW + timedelta(minutes=5), SETTINGS) is False
    assert get_user(engine, uid) == before  # neither counted nor extended


def test_count_never_exceeds_the_limit(engine) -> None:
    uid = add_user(engine)
    fail_times(engine, uid, 12)
    assert get_user(engine, uid).failed_login_count == 5


def test_expired_lock_restarts_count_at_one(engine) -> None:
    uid = add_user(engine)
    fail_times(engine, uid, 5)
    later = NOW + timedelta(minutes=15, seconds=1)
    assert record_failure(engine, uid, later, SETTINGS) is True
    view = get_user(engine, uid)
    assert view.failed_login_count == 1 and view.locked_until is None


def test_lock_boundary_exactly_at_expiry_counts_as_expired(engine) -> None:
    uid = add_user(engine)
    fail_times(engine, uid, 5)
    assert record_failure(engine, uid, NOW + timedelta(minutes=15), SETTINGS) is True
    assert get_user(engine, uid).failed_login_count == 1


def test_expired_lock_with_limit_of_one_relocks(engine) -> None:
    uid = add_user(engine)
    one = LockoutSettings(max_failures=1, lock_minutes=15)
    record_failure(engine, uid, NOW, one)
    later = NOW + timedelta(minutes=20)
    assert record_failure(engine, uid, later, one) is True
    assert get_user(engine, uid).locked_until == later + timedelta(minutes=15)


def test_inactive_account_is_not_counted(engine) -> None:
    uid = add_user(engine)
    deactivate_user_by_id(engine, uid)
    assert record_failure(engine, uid, NOW, SETTINGS) is False
    assert get_user(engine, uid).failed_login_count == 0


def test_success_resets_count(engine) -> None:
    uid = add_user(engine)
    fail_times(engine, uid, 3)
    assert record_success(engine, uid, NOW) is True
    assert get_user(engine, uid).failed_login_count == 0


def test_success_update_reports_no_row_when_locked(engine) -> None:
    uid = add_user(engine)
    fail_times(engine, uid, 5)
    assert record_success(engine, uid, NOW + timedelta(minutes=1)) is False
    assert get_user(engine, uid).locked_until is not None


def test_success_after_expiry_clears_old_lock(engine) -> None:
    uid = add_user(engine)
    fail_times(engine, uid, 5)
    assert record_success(engine, uid, NOW + timedelta(minutes=16)) is True
    view = get_user(engine, uid)
    assert view.locked_until is None and view.failed_login_count == 0


def test_unlock_clears_both_fields_and_nothing_else(engine) -> None:
    uid = add_user(engine)
    fail_times(engine, uid, 5)
    before = get_user(engine, uid)
    assert unlock(engine, uid) is True
    after = get_user(engine, uid)
    assert (after.failed_login_count, after.locked_until) == (0, None)
    assert (after.password_hash, after.is_active, after.auth_version) == (
        before.password_hash, before.is_active, before.auth_version)


def test_unlock_unknown_id_changes_nothing(engine) -> None:
    assert unlock(engine, 12345) is False


def test_auth_version_increments_are_atomic_across_connections(engine, db_file) -> None:
    uid = add_user(engine)
    other = make_engine(db_file)
    assert increment_auth_version(engine, uid) and increment_auth_version(other, uid)
    assert get_user(engine, uid).auth_version == 2
    other.dispose()


def test_increment_with_expected_value_is_conditional(engine) -> None:
    uid = add_user(engine)
    assert increment_auth_version(engine, uid, expected=5) is False
    assert increment_auth_version(engine, uid, expected=0) is True
    assert get_user(engine, uid).auth_version == 1


def test_two_failure_increments_from_separate_connections_both_counted(engine, db_file) -> None:
    uid = add_user(engine)
    other = make_engine(db_file)
    record_failure(engine, uid, NOW, SETTINGS)
    record_failure(other, uid, NOW, SETTINGS)
    assert get_user(engine, uid).failed_login_count == 2
    other.dispose()


def test_deactivate_sets_flag_and_bumps_version(engine) -> None:
    uid = add_user(engine)
    assert deactivate_user_by_id(engine, uid) is True
    view = get_user(engine, uid)
    assert view.is_active is False and view.auth_version == 1
