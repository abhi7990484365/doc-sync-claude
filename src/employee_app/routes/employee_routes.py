"""C-3 Add Employee routes with Post/Redirect/Get (D-6). No SQL, no rules."""

from flask import Blueprint, abort, flash, get_flashed_messages, redirect, render_template, request, url_for
from flask_login import current_user
from werkzeug.wrappers import Response

from employee_app.auth.guard import protected
from employee_app.extensions import get_state
from employee_app.services.employee import CreateStatus, create_employee
from employee_app.validation import FIELD_NAMES

bp = Blueprint("employees", __name__)

FLASH_CREATED = "employee_created"  # fixed key only; the text lives in the template


def _form_page(values: dict[str, str], errors: dict[str, str], created: bool = False) -> str:
    return render_template(
        "employee_form.html",
        values=values,
        errors=errors,
        created=created,
        departments=get_state().settings.departments,
    )


@bp.route("/employees/new", methods=["GET"])
@protected
def new_employee() -> str:
    created = FLASH_CREATED in get_flashed_messages()
    return _form_page({name: "" for name in FIELD_NAMES}, {}, created)


@bp.route("/employees/new", methods=["POST"])
@protected
def create_new_employee() -> Response | str:
    state = get_state()
    result = create_employee(state.engine, state.settings, request.form, int(current_user.get_id()))
    if result.status is CreateStatus.CREATED:
        flash(FLASH_CREATED)
        return redirect(url_for("employees.new_employee"), code=303)
    if result.status is CreateStatus.INVALID:
        return _form_page(result.values, result.errors)
    abort(500)
