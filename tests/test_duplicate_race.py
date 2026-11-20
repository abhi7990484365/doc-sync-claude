"""TASK-035 (mandatory): duplicate-email race with a defined outcome (NR-14, E-8, D-25).

Two real connections (own engines) to a temporary FILE database with the
pre-check bypassed so both insert. Asserted outcome: exactly one creation; the
loser sees the email-in-use error (D-25 intent), not the generic failure.
"""

import threading

from employee_app.services.employee import CreateStatus, create_employee
from employee_app.validation.messages import EMAIL_IN_USE
from tests.conftest import make_engine
from tests.web_helpers import employee_counts, valid_form, web_settings


def race(engine, db_file, admin_id, monkeypatch, case_b: str):  # type: ignore[no-untyped-def]
    monkeypatch.setattr("employee_app.services.employee._pre_check", lambda *_a: False)  # bypass
    settings = web_settings(db_file)
    engines = [make_engine(db_file, busy=10.0), make_engine(db_file, busy=10.0)]
    barrier = threading.Barrier(2)
    results: list = [None, None]
    emails = ["race.person@example.com", case_b]

    def worker(i: int) -> None:
        barrier.wait(10)
        results[i] = create_employee(engines[i], settings, valid_form(email=emails[i]), admin_id)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(30)
    for e in engines:
        e.dispose()
    return results


def check_outcome(engine, results) -> None:  # type: ignore[no-untyped-def]
    statuses = sorted(r.status.value for r in results)
    assert statuses == ["created", "invalid"], statuses  # a generic "failed" here is a defect
    loser = next(r for r in results if r.status is CreateStatus.INVALID)
    assert loser.errors == {"email": EMAIL_IN_USE}
    assert employee_counts(engine) == (1, 1)


def test_same_email_race_loser_sees_email_in_use(engine, db_file, admin_id, fixed_clock, monkeypatch) -> None:
    check_outcome(engine, race(engine, db_file, admin_id, monkeypatch, "race.person@example.com"))


def test_case_only_race_loser_sees_email_in_use(engine, db_file, admin_id, fixed_clock, monkeypatch) -> None:
    check_outcome(engine, race(engine, db_file, admin_id, monkeypatch, "RACE.PERSON@EXAMPLE.COM"))


def test_race_repeated_gives_the_same_defined_outcome(engine, db_file, admin_id, fixed_clock, monkeypatch) -> None:
    for round_number in range(5):
        local = f"repeat{round_number}@example.com"
        monkeypatch.setattr("employee_app.services.employee._pre_check", lambda *_a: False)
        settings = web_settings(db_file)
        engines = [make_engine(db_file, busy=10.0) for _ in range(2)]
        barrier = threading.Barrier(2)
        out: list = [None, None]

        def worker(i: int) -> None:
            barrier.wait(10)
            out[i] = create_employee(engines[i], settings, valid_form(email=local), admin_id)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(2)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(30)
        for e in engines:
            e.dispose()
        assert sorted(r.status.value for r in out) == ["created", "invalid"]
    assert employee_counts(engine) == (5, 5)


def test_non_email_integrity_error_returns_the_generic_failure(engine, db_file, fixed_clock) -> None:
    result = create_employee(engine, web_settings(db_file), valid_form(), admin_id=424242)  # FK violation
    assert result.status is CreateStatus.FAILED and not result.errors
    assert employee_counts(engine) == (0, 0)
