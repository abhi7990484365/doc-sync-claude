"""TASK-032: templates and static assets (FR-2, FR-11, NFR-5)."""

import re

from tests.web_helpers import TEST_DEPARTMENTS, post_employee, valid_form


def test_form_has_seven_inputs_dropdown_csrf_field_and_logout_form(logged_in) -> None:
    html = logged_in.get("/employees/new").get_data(as_text=True)
    assert html.count('name="csrf_token"') == 2  # add form + logout form
    assert '<select id="department" name="department"' in html
    assert 'action="/logout"' in html
    options = re.findall(r'<option value="([^"]*)"', html)
    assert options == [""] + list(TEST_DEPARTMENTS)


def test_user_input_is_escaped(logged_in) -> None:
    payload = '"><script>alert(1)</script>'
    html = post_employee(logged_in, valid_form(first_name=payload, email="bad")).get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html


def test_no_inline_script_and_only_same_origin_assets(logged_in) -> None:
    for html in (logged_in.get("/employees/new").get_data(as_text=True),
                 logged_in.get("/login").get_data(as_text=True)):
        for tag in re.findall(r"<script[^>]*>", html):
            assert "src=" in tag
        assert "onclick" not in html and "http://" not in html and "https://" not in html


def test_static_assets_are_served(client) -> None:
    assert client.get("/static/style.css").status_code == 200
    assert client.get("/static/form.js").status_code == 200


def test_page_works_without_script_the_form_posts_normally(logged_in) -> None:
    html = logged_in.get("/employees/new").get_data(as_text=True)
    assert re.search(r'<form method="post" action="/employees/new"', html)
    assert "<noscript" not in html  # nothing depends on the script


def test_login_page_has_username_password_and_token(client) -> None:
    html = client.get("/login").get_data(as_text=True)
    for needle in ('name="username"', 'name="password"', 'name="csrf_token"', 'type="password"'):
        assert needle in html
