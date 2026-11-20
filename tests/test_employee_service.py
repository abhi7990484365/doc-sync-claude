"""TASK-030: employee service (FR-5, FR-8, FR-13, FR-17; N-11, N-19, AC-05, AC-05b)."""

import logging

import pytest

from employee_app.db.errors import StorageError
from employee_app.services.employee import CreateStatus, create_employee
from employee_app.validation.messages import EMAIL_IN_USE
from tests.web_helpers import employee_counts, valid_form, web_settings


@pytest.fixture
def settings(db_file):  # type: ignore[no-untyped-def]
    return web_settings(db_file)


@pytest.fixture
def setup(engine, admin_id, fixed_clock, settings):  # type: ignore[no-untyped-def]
    return engine, settings, admin_id


def test_valid_creation_writes_employee_and_audit(setup) -> None:
    engine, settings, admin = setup
    result = create_employee(engine, settings, valid_form(), admin)
    assert result.status is CreateStatus.CREATED and result.employee_id
    assert employee_counts(engine) == (1, 1)


def test_invalid_input_writes_nothing_and_no_audit_row(setup) -> None:  # N-11
    engine, settings, admin = setup
    result = create_employee(engine, settings, valid_form(email="nope", phone="1"), admin)
    assert result.status is CreateStatus.INVALID and set(result.errors) == {"email", "phone"}
    assert employee_counts(engine) == (0, 0)


def test_values_are_kept_for_redisplay(setup) -> None:
    engine, settings, admin = setup
    result = create_employee(engine, settings, valid_form(first_name=" Kept ", email="bad"), admin)
    assert result.values["first_name"] == "Kept"


def test_duplicate_email_is_rejected_with_the_email_in_use_error(setup) -> None:  # AC-05
    engine, settings, admin = setup
    create_employee(engine, settings, valid_form(), admin)
    result = create_employee(engine, settings, valid_form(), admin)
    assert result.status is CreateStatus.INVALID and result.errors == {"email": EMAIL_IN_USE}
    assert employee_counts(engine) == (1, 1)


def test_case_only_duplicate_is_rejected(setup) -> None:  # AC-05b
    engine, settings, admin = setup
    create_employee(engine, settings, valid_form(email="Test.Person@Example.com"), admin)
    result = create_employee(engine, settings, valid_form(email="TEST.PERSON@EXAMPLE.COM"), admin)
    assert result.errors == {"email": EMAIL_IN_USE}


def test_resubmission_shows_the_duplicate_error(setup) -> None:  # N-19, FR-17
    engine, settings, admin = setup
    form = valid_form()
    assert create_employee(engine, settings, form, admin).status is CreateStatus.CREATED
    assert create_employee(engine, settings, form, admin).errors == {"email": EMAIL_IN_USE}


def test_department_outside_the_list_is_invalid(setup) -> None:
    engine, settings, admin = setup
    result = create_employee(engine, settings, valid_form(department="Elsewhere"), admin)
    assert set(result.errors) == {"department"}


def test_past_joining_date_uses_the_clock(setup, fixed_clock) -> None:
    engine, settings, admin = setup
    fixed_clock.advance(days=1)  # today is now 2026-11-21
    assert "joining_date" in create_employee(engine, settings, valid_form(), admin).errors


def test_storage_error_in_precheck_is_a_generic_failure(setup, monkeypatch) -> None:
    engine, settings, admin = setup

    def broken(*_a: object) -> bool:
        raise StorageError("OperationalError")

    monkeypatch.setattr("employee_app.services.employee._pre_check", broken)
    assert create_employee(engine, settings, valid_form(), admin).status is CreateStatus.FAILED
    assert employee_counts(engine) == (0, 0)


def test_storage_error_in_write_is_a_generic_failure(setup, monkeypatch) -> None:
    engine, settings, admin = setup

    def broken(*_a: object) -> int:
        raise StorageError("OperationalError")

    monkeypatch.setattr("employee_app.services.employee.insert_employee_with_audit", broken)
    assert create_employee(engine, settings, valid_form(), admin).status is CreateStatus.FAILED


def test_non_email_integrity_error_is_a_generic_failure(setup) -> None:
    engine, settings, _admin = setup
    # unknown admin id: the foreign key fails, email does not exist afterwards
    result = create_employee(engine, settings, valid_form(), 99999)
    assert result.status is CreateStatus.FAILED and employee_counts(engine) == (0, 0)


def test_service_logs_ids_and_counts_without_values(setup, caplog) -> None:
    engine, settings, admin = setup
    with caplog.at_level(logging.INFO, logger="employee_app"):
        create_employee(engine, settings, valid_form(), admin)
        create_employee(engine, settings, valid_form(email="bad", first_name=""), admin)
    text = " ".join(r.getMessage() for r in caplog.records)
    assert "employee_created employee_id=1 admin_id=" in text and "validation_failed count=2" in text
    for personal in ("Test", "Person", "example.com", "5551234567"):
        assert personal not in text


def test_service_does_not_touch_the_database_outside_c6() -> None:
    import employee_app.services.employee as module
    from tests.helpers import imported_modules

    names = imported_modules(module)
    assert not [n for n in names if n.startswith(("sqlalchemy.orm", "sqlite3"))]
    assert "sqlalchemy" not in names
