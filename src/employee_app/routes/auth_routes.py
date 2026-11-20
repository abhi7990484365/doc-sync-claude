"""C-3 login and logout routes (HTTP only)."""

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user
from werkzeug.wrappers import Response

from employee_app import clock
from employee_app.auth.guard import protected
from employee_app.auth.login import attempt_login
from employee_app.auth.session import end_session, start_session
from employee_app.db.users import increment_auth_version
from employee_app.extensions import csrf, get_state

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login() -> Response | str:
    """Public route: CSRF only on POST. Every failure gives the same 200 page."""
    if request.method == "GET":
        return render_template("login.html", failed=False)
    csrf.protect()
    user = attempt_login(get_state(), request.form.get("username", ""), request.form.get("password", ""))
    if user is None:
        return render_template("login.html", failed=True)
    start_session(user, clock.utc_now())
    return redirect(url_for("employees.new_employee"), code=303)  # `next` is ignored (D-17)


@bp.route("/logout", methods=["POST"])
@protected
def logout() -> Response:
    """Authenticated and CSRF checked: atomically bump auth_version, clear session."""
    increment_auth_version(get_state().engine, int(current_user.get_id()))
    end_session()
    return redirect(url_for("auth.login"), code=303)
