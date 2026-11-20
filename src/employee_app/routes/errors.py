"""C-3 response headers and error handlers (D-22, NFR-4).

Error pages are plain, contain no internals and offer a link to the login
page. A 401 carries no ``WWW-Authenticate`` header (OQ-A15, approved).
"""

import logging
import time

from flask import Flask, Response, g, render_template, request
from flask_wtf.csrf import CSRFError
from werkzeug.exceptions import HTTPException

from employee_app.logging_setup import log_event, log_server_error

MESSAGES = {
    400: "The request could not be processed.",
    401: "You are not signed in, or your session has ended.",
    403: "You are not allowed to do that.",
    404: "The page was not found.",
    405: "That action is not allowed here.",
    413: "The submitted data is too large.",
    500: "Something went wrong. Please try again later.",
}
GENERIC = MESSAGES[500]

CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self'; "
    "form-action 'self'; frame-ancestors 'none'; base-uri 'none'"
)


def error_page(status: int) -> Response:
    body = render_template("error.html", status=status, message=MESSAGES.get(status, GENERIC))
    return Response(body, status=status, mimetype="text/html")


def _handle_http(error: HTTPException) -> Response:
    status = error.code or 500
    return error_page(status if status in MESSAGES else 500)


def _handle_csrf(_error: CSRFError) -> Response:
    return error_page(403)


def _handle_unexpected(error: Exception) -> Response:
    log_server_error("unhandled_exception", error, category=type(error).__name__)
    return error_page(500)


def add_security_headers(response: Response) -> Response:
    """Headers on every response; no-store on everything but static files."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = CSP
    if request.endpoint != "static":
        response.headers["Cache-Control"] = "no-store"
    return response


def _start_timer() -> None:
    g.request_started = time.perf_counter()


def _log_if_slow(response: Response, threshold_seconds: float) -> Response:
    started = g.get("request_started")
    if started is not None and time.perf_counter() - started > threshold_seconds:
        log_event(logging.WARNING, "slow_request", duration_ms=int((time.perf_counter() - started) * 1000))
    return response


def register(app: Flask, hsts: bool, slow_seconds: float) -> None:
    app.register_error_handler(HTTPException, _handle_http)
    app.register_error_handler(CSRFError, _handle_csrf)
    app.register_error_handler(Exception, _handle_unexpected)
    app.before_request(_start_timer)

    @app.after_request
    def _after(response: Response) -> Response:
        response = add_security_headers(response)
        if hsts:
            response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return _log_if_slow(response, slow_seconds)
