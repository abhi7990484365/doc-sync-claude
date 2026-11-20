"""TASK-022 (NR-13): unlock-user integration. Covers FR-18, AC-16, AC-17, P-14, P-15, N-20, E-18.

Accounts are created through the C-10 code path (create-user) and the clock is pinned.
"""

import secrets
import threading

from employee_app.config import LockoutSettings
from employee_app.db.lockout import record_failure, unlock
from employee_app.db.users import find_user_by_username
from tests.cmd_helpers import cmd_env, create_user_input, run_cli
from tests.conftest import make_engine
from tests.web_helpers import login

WRONG = "definitely-not-the-login-value"


def create(db_file, name: str) -> str:  # type: ignore[no-untyped-def]
    secret = secrets.token_urlsafe(18)
    assert run_cli(["create-user"], cmd_env(db_file), create_user_input(name, secret)).exit_code == 0
    return secret


def lock_through_login(client, name: str) -> None:  # type: ignore[no-untyped-def]
    for _ in range(5):
        login(client, name, WRONG)


def test_a_after_unlock_the_correct_password_logs_in_ac16_p14(app, db_file, engine, fixed_clock) -> None:
    secret = create(db_file, "locked.user")
    client = app.test_client()
    lock_through_login(client, "locked.user")
    assert login(client, "locked.user", secret).status_code == 200  # still locked
    assert run_cli(["unlock-user", "locked.user"], cmd_env(db_file)).exit_code == 0
    assert login(client, "locked.user", secret).status_code == 303
    assert client.get("/employees/new").status_code == 200


def test_b_password_hash_is_identical_before_and_after_unlock_ac17(db_file, engine, fixed_clock) -> None:
    create(db_file, "plain.user")
    before = find_user_by_username(engine, "plain.user")
    assert run_cli(["unlock-user", "plain.user"], cmd_env(db_file)).exit_code == 0
    assert find_user_by_username(engine, "plain.user").password_hash == before.password_hash


def test_c_deactivated_and_locked_account_stays_blocked_after_unlock_n20(app, db_file, engine, fixed_clock) -> None:
    secret = create(db_file, "both.user")
    client = app.test_client()
    lock_through_login(client, "both.user")
    assert run_cli(["deactivate-user", "both.user"], cmd_env(db_file)).exit_code == 0
    assert run_cli(["unlock-user", "both.user"], cmd_env(db_file)).exit_code == 0
    user = find_user_by_username(engine, "both.user")
    assert (user.is_active, user.failed_login_count, user.locked_until) == (False, 0, None)
    response = login(client, "both.user", secret)
    assert response.status_code == 200 and client.get("/employees/new").status_code == 302


def test_e18_unknown_username_changes_nothing(db_file, engine) -> None:
    create(db_file, "kept.user")
    before = find_user_by_username(engine, "kept.user")
    result = run_cli(["unlock-user", "unknown.user"], cmd_env(db_file))
    assert result.exit_code != 0
    assert find_user_by_username(engine, "kept.user") == before


def test_d_unlock_racing_a_concurrent_failure_ends_in_a_defined_state(engine, db_file, fixed_clock) -> None:
    limit = LockoutSettings(max_failures=5, lock_minutes=15)
    allowed = {(0, None), (1, None)}  # unlock last, or failure counted after the unlock
    for round_number in range(10):
        from tests.conftest import add_user

        name = f"race{round_number}"
        uid = add_user(engine, name)
        for _ in range(4):
            record_failure(engine, uid, fixed_clock.now, limit)
        engines = [make_engine(db_file, busy=10.0), make_engine(db_file, busy=10.0)]
        barrier = threading.Barrier(2)

        def do_unlock() -> None:
            barrier.wait(10)
            unlock(engines[0], uid)

        def do_failure() -> None:
            barrier.wait(10)
            record_failure(engines[1], uid, fixed_clock.now, limit)

        threads = [threading.Thread(target=do_unlock), threading.Thread(target=do_failure)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(30)
        user = find_user_by_username(engine, name)
        state = (user.failed_login_count, user.locked_until)
        # Start: count 4, no lock. Failure then unlock gives (0, None); unlock then
        # failure gives (1, None). A lock with count 0, or count 5 without a
        # lock, can never appear.
        assert state in allowed, state
        for e in engines:
            e.dispose()
