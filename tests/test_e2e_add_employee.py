"""TASK-038: end-to-end acceptance tests AC-01 to AC-10 (also N/P ids named in each docstring).

A user is created through the C-10 code path (the create-user command); the
form factory ``valid_form`` builds a valid form and each case overrides one field.
"""

import secrets
from datetime import date

import pytest
from sqlalchemy import select

from employee_app.db.engine import session_scope
from employee_app.db.models import AuditRecord, Employee
from tests.cmd_helpers import cmd_env, create_user_input, run_cli
from tests.web_helpers import (TEST_DEPARTMENTS, employee_counts, login, page_token, post_employee, valid_form)


@pytest.fixture
def session_client(engine, db_file, app):  # type: ignore[no-untyped-def]
    secret = secrets.token_urlsafe(18)
    result = run_cli(["create-user"], cmd_env(db_file), create_user_input("hr.admin", secret))
    assert result.exit_code == 0, result.output
    client = app.test_client()
    assert login(client, "hr.admin", secret).status_code == 303
    return client


def stored_employees(engine) -> list[Employee]:  # type: ignore[no-untyped-def]
    with session_scope(engine) as s:
        return list(s.scalars(select(Employee)))


def test_ac01_p1_form_shows_seven_fields(session_client) -> None:
    html = session_client.get("/employees/new").get_data(as_text=True)
    for name in ("first_name", "last_name", "email", "phone", "department", "job_title", "joining_date"):
        assert f'name="{name}"' in html


def test_ac02_p2_to_p4_valid_creation_stores_trimmed_normalised_values(session_client, engine) -> None:
    response = post_employee(session_client, valid_form(first_name="  Ann ", email=" Ann.Lee@Example.COM "))
    assert response.status_code == 303
    (row,) = stored_employees(engine)
    assert (row.first_name, row.email, row.email_normalized) == ("Ann", "Ann.Lee@Example.COM", "ann.lee@example.com")
    assert row.phone == "5551234567" and row.joining_date == date(2026, 11, 20)


@pytest.mark.parametrize("field", ["first_name", "last_name", "email", "phone", "department", "job_title", "joining_date"])
def test_ac03_n1_n2_each_empty_field_is_an_error(session_client, engine, field: str) -> None:
    html = post_employee(session_client, valid_form(**{field: "   "})).get_data(as_text=True)
    assert f'id="{field}-error"' in html and employee_counts(engine) == (0, 0)


def test_n1_all_empty_form_shows_seven_errors(session_client, engine) -> None:
    html = post_employee(session_client, {k: "" for k in valid_form()}).get_data(as_text=True)
    assert html.count('class="field-error"') == 7 and employee_counts(engine) == (0, 0)


@pytest.mark.parametrize("email", ["plain", "a@b", "a b@c.com", "@c.com"])
def test_ac04_n3_invalid_email(session_client, engine, email: str) -> None:
    assert 'id="email-error"' in post_employee(session_client, valid_form(email=email)).get_data(as_text=True)
    assert employee_counts(engine) == (0, 0)


def test_ac05_n4_duplicate_email(session_client, engine) -> None:
    post_employee(session_client, valid_form())
    html = post_employee(session_client, valid_form(first_name="Other")).get_data(as_text=True)
    assert "already in use" in html and employee_counts(engine) == (1, 1)


def test_ac05b_n4b_case_only_duplicate_email(session_client, engine) -> None:
    post_employee(session_client, valid_form(email="Same@Example.com"))
    html = post_employee(session_client, valid_form(email="SAME@example.COM")).get_data(as_text=True)
    assert "already in use" in html and employee_counts(engine) == (1, 1)


@pytest.mark.parametrize("phone", ["5551234567", "555-123-4567", "(555) 123-4567"])
def test_p3_p6_valid_phone_formats_store_ten_digits(session_client, engine, phone: str) -> None:
    assert post_employee(session_client, valid_form(phone=phone)).status_code == 303
    assert stored_employees(engine)[0].phone == "5551234567"


@pytest.mark.parametrize("phone", ["555123456", "55512345678", "+1 555 123 4567", "abcdefghij"])
def test_ac06_n5_invalid_phone(session_client, engine, phone: str) -> None:
    assert 'id="phone-error"' in post_employee(session_client, valid_form(phone=phone)).get_data(as_text=True)
    assert employee_counts(engine) == (0, 0)


def test_ac06b_phone_with_parentheses_is_accepted(session_client) -> None:
    assert post_employee(session_client, valid_form(phone="(555) 123-4567")).status_code == 303


def test_ac07_n6_yesterday_rejected(session_client, engine) -> None:
    html = post_employee(session_client, valid_form(joining_date="2026-11-19")).get_data(as_text=True)
    assert 'id="joining_date-error"' in html and employee_counts(engine) == (0, 0)


@pytest.mark.parametrize("joining", ["2026-11-20", "2026-11-21", "2099-01-01"])
def test_ac07b_p5_p13_today_tomorrow_and_far_future_accepted(session_client, joining: str) -> None:
    assert post_employee(session_client, valid_form(joining_date=joining)).status_code == 303


def test_e11_impossible_date_is_a_field_error(session_client) -> None:
    assert 'id="joining_date-error"' in post_employee(
        session_client, valid_form(joining_date="2026-02-30")).get_data(as_text=True)


@pytest.mark.parametrize("department", TEST_DEPARTMENTS)
def test_p7_each_dropdown_choice_is_accepted(session_client, department: str) -> None:
    assert post_employee(session_client, valid_form(department=department, email=f"{secrets.token_hex(3)}@example.com")
                         ).status_code == 303


def test_ac09_p8_stay_on_a_cleared_form_with_a_message(session_client) -> None:
    response = post_employee(session_client, valid_form())
    assert response.status_code == 303
    html = session_client.get(response.headers["Location"]).get_data(as_text=True)
    assert "Employee added successfully." in html and 'value="Test"' not in html


def test_ac10_p9_one_audit_row_on_success_with_creator_and_time(session_client, engine, fixed_clock) -> None:
    post_employee(session_client, valid_form())
    with session_scope(engine) as s:
        audit = s.scalars(select(AuditRecord)).one()
        assert audit.created_at == fixed_clock.now and audit.created_by_user_id


def test_n11_no_audit_row_on_any_rejection(session_client, engine) -> None:
    post_employee(session_client, valid_form(email="bad"))
    post_employee(session_client, valid_form())
    post_employee(session_client, valid_form())  # duplicate
    assert employee_counts(engine) == (1, 1)


def test_n10_several_errors_are_shown_at_once_and_values_kept(session_client) -> None:
    html = post_employee(session_client, valid_form(email="bad", phone="1", job_title="Keep Me")).get_data(as_text=True)
    assert 'id="email-error"' in html and 'id="phone-error"' in html and 'value="Keep Me"' in html


@pytest.mark.parametrize("length, ok", [(1, True), (100, True), (101, False)])
def test_p12_n18_name_length_boundaries(session_client, length: int, ok: bool) -> None:
    response = post_employee(session_client, valid_form(first_name="a" * length))
    assert (response.status_code == 303) is ok


@pytest.mark.parametrize("length, ok", [(254, True), (255, False)])
def test_p12_n18_email_length_boundaries(session_client, length: int, ok: bool) -> None:
    local = "a" * (length - len("@b.co"))
    assert (post_employee(session_client, valid_form(email=f"{local}@b.co")).status_code == 303) is ok


def test_n19_resubmitting_the_same_data_shows_the_duplicate_error(session_client) -> None:
    form = valid_form()
    token = page_token(session_client, "/employees/new")
    assert post_employee(session_client, form, token).status_code == 303
    assert "already in use" in post_employee(session_client, form, token).get_data(as_text=True)
