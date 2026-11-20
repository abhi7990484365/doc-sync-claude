"""TASK-033 (mandatory): lockout under concurrency with real connections.

Every thread uses its own engine (its own SQLite connection) on a temporary
FILE database. Threads are released together through a barrier; no sleep is
used for synchronisation.
"""

import threading
from collections.abc import Callable
from datetime import timedelta

import pytest

from employee_app.config import LockoutSettings
from employee_app.db.lockout import record_failure
from employee_app.db.users import find_user_by_username
from employee_app.extensions import AppState
from tests.conftest import add_user, login_secret_for_tests, make_engine
from tests.web_helpers import web_settings

THREADS = 8
LIMIT = LockoutSettings(max_failures=5, lock_minutes=15)
WRONG = "definitely-not-the-login-value"


def run_together(jobs: list[Callable[[], object]]) -> list[object]:
    barrier = threading.Barrier(len(jobs))
    results: list[object] = [None] * len(jobs)
    errors: list[BaseException] = []

    def runner(index: int, job: Callable[[], object]) -> None:
        try:
            barrier.wait(10)
            results[index] = job()
        except BaseException as exc:  # noqa: BLE001 - surfaced below
            errors.append(exc)

    threads = [threading.Thread(target=runner, args=(i, j)) for i, j in enumerate(jobs)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(30)
    assert not errors, errors
    return results


@pytest.fixture
def engines(db_file, engine, fixed_clock):  # type: ignore[no-untyped-def]
    many = [make_engine(db_file, busy=10.0) for _ in range(THREADS)]
    yield many
    for e in many:
        e.dispose()


def test_concurrent_failures_lose_no_increment_and_set_the_lock_once(engine, engines, fixed_clock) -> None:
    uid = add_user(engine)
    now = fixed_clock.now
    results = run_together([lambda e=e: record_failure(e, uid, now, LIMIT) for e in engines])
    changed = [r for r in results if r]
    user = find_user_by_username(engine, "admin1")
    assert len(changed) == 5  # exactly 5 counted: no lost increment, none past the limit
    assert user.failed_login_count == 5
    assert user.locked_until == now + timedelta(minutes=15)  # set once, not extended
    assert len([r for r in results if not r]) == THREADS - 5  # the rest saw the lock and changed nothing


def test_guesses_evaluated_beyond_the_limit_do_not_exceed_requests_in_flight(engine, engines, fixed_clock, monkeypatch) -> None:
    from employee_app.auth import login as login_module

    add_user(engine)
    evaluated = []
    real = login_module.verify_password

    def counting(stored: str, candidate: str) -> bool:
        evaluated.append(candidate)
        return real(stored, candidate)

    monkeypatch.setattr(login_module, "verify_password", counting)
    settings = web_settings(engine.url.database)
    states = [AppState(settings, e) for e in engines]
    run_together([lambda s=s: login_module.attempt_login(s, "admin1", WRONG) for s in states])
    user = find_user_by_username(engine, "admin1")
    assert user.failed_login_count == 5 and user.locked_until is not None
    assert len(evaluated) - 5 <= THREADS  # overshoot bounded by the requests in flight
    assert len(evaluated) <= THREADS


def test_correct_value_racing_the_fifth_failure_never_gets_a_session_once_locked(engine, engines, fixed_clock) -> None:
    from employee_app.auth import login as login_module

    settings = web_settings(engine.url.database)
    secret = login_secret_for_tests()
    for round_number in range(6):
        name = f"racer{round_number}"
        uid = add_user(engine, name)
        for _ in range(4):
            record_failure(engine, uid, fixed_clock.now, LIMIT)
        fifth, correct = (AppState(settings, engines[0]), AppState(settings, engines[1]))
        outcome = run_together([
            lambda: login_module.attempt_login(fifth, name, WRONG),
            lambda: login_module.attempt_login(correct, name, secret),
        ])
        user = find_user_by_username(engine, name)
        got_session = outcome[1] is not None
        # Invariant: a login that succeeded cannot coexist with a lock.
        assert not (got_session and user.locked_until is not None)
        # And the pair (count, lock) is one of the defined end states.
        assert (user.failed_login_count, user.locked_until is not None) in {(5, True), (1, False)}


def test_forced_interleaving_success_update_fails_after_the_lock_exists(engine, fixed_clock, monkeypatch) -> None:
    """Deterministic version of the race: the correct-value request has read the
    account as unlocked, then the 5th failure sets the lock, then the success
    update must change no row and the login must be rejected."""
    from employee_app.auth import login as login_module

    uid = add_user(engine)
    for _ in range(4):
        record_failure(engine, uid, fixed_clock.now, LIMIT)
    real_find = login_module.find_user_by_username

    def find_then_lock(eng, normalized):  # type: ignore[no-untyped-def]
        view = real_find(eng, normalized)  # stale: not locked yet
        record_failure(eng, uid, fixed_clock.now, LIMIT)  # the 5th failure lands now
        return view

    monkeypatch.setattr(login_module, "find_user_by_username", find_then_lock)
    state = AppState(web_settings(engine.url.database), engine)
    assert login_module.attempt_login(state, "admin1", login_secret_for_tests()) is None
    assert find_user_by_username(engine, "admin1").locked_until is not None
