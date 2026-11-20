"""TASK-031: Add Employee routes with Post/Redirect/Get (P-1, P-8, FR-9, FR-10)."""

import re

from tests.web_helpers import TEST_DEPARTMENTS, employee_counts, page_token, post_employee, valid_form

FIELDS = ["first_name", "last_name", "email", "phone", "department", "job_title", "joining_date"]


def test_get_shows_the_form_with_seven_fields_and_the_department_list(logged_in) -> None:  # P-1
    html = logged_in.get("/employees/new").get_data(as_text=True)
    for name in FIELDS:
        assert f'name="{name}"' in html
    for department in TEST_DEPARTMENTS:
        assert f">{department}</option>" in html


def test_success_redirects_with_303_to_an_empty_form_and_one_time_message(logged_in, engine) -> None:  # P-8
    response = post_employee(logged_in, valid_form())
    assert response.status_code == 303 and response.headers["Location"].endswith("/employees/new")
    page = logged_in.get("/employees/new").get_data(as_text=True)
    assert "Employee added successfully." in page
    assert 'value="Test"' not in page and "test.person@example.com" not in page
    assert "Employee added successfully." not in logged_in.get("/employees/new").get_data(as_text=True)
    assert employee_counts(engine) == (1, 1)


def test_refresh_after_success_does_not_resubmit(logged_in, engine) -> None:
    post_employee(logged_in, valid_form())
    logged_in.get("/employees/new")
    logged_in.get("/employees/new")
    assert employee_counts(engine) == (1, 1)


def test_invalid_form_returns_200_with_every_error_and_entered_values(logged_in, engine) -> None:  # N-10
    form = valid_form(first_name="  ", email="bad", phone="123", joining_date="2000-01-01",
                      last_name="Kept Name")
    response = post_employee(logged_in, form)
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    for name in ("first_name", "email", "phone", "joining_date"):
        assert f'id="{name}-error"' in html
    assert 'id="last_name-error"' not in html
    assert 'value="Kept Name"' in html and 'value="bad"' in html
    assert employee_counts(engine) == (0, 0)


def test_department_outside_the_list_is_rejected(logged_in, engine) -> None:
    html = post_employee(logged_in, valid_form(department="Not In List")).get_data(as_text=True)
    assert 'id="department-error"' in html and employee_counts(engine) == (0, 0)


def test_selected_department_is_kept_on_error(logged_in) -> None:
    html = post_employee(logged_in, valid_form(department=TEST_DEPARTMENTS[1], email="bad")).get_data(as_text=True)
    assert re.search(rf'<option value="{TEST_DEPARTMENTS[1]}" selected>', html)


def test_duplicate_email_shows_field_error(logged_in) -> None:
    post_employee(logged_in, valid_form())
    html = post_employee(logged_in, valid_form()).get_data(as_text=True)
    assert 'id="email-error"' in html and "already in use" in html


def test_storage_failure_gives_generic_500_page(logged_in, monkeypatch) -> None:
    from employee_app.db.errors import StorageError

    def broken(*_a: object, **_k: object) -> int:
        raise StorageError("OperationalError")

    monkeypatch.setattr("employee_app.services.employee.insert_employee_with_audit", broken)
    response = post_employee(logged_in, valid_form())
    assert response.status_code == 500 and "OperationalError" not in response.get_data(as_text=True)


def test_page_is_not_reachable_without_login(client) -> None:
    assert client.get("/employees/new").status_code == 302


def test_routes_contain_no_sql_and_no_rules() -> None:
    import employee_app.routes.employee_routes as module
    from tests.helpers import imported_modules

    names = " ".join(imported_modules(module))
    assert "sqlalchemy" not in names and "employee_app.db" not in names and "validation.phone" not in names
    assert page_token  # helper import used
