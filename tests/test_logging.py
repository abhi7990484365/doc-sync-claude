"""TASK-007: logging helpers carry only ids and category tokens."""

import logging

import pytest

from employee_app.logging_setup import configure_logging, format_event, get_logger, log_event, log_server_error


def test_event_line_has_only_ids_and_categories(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="employee_app"):
        log_event(logging.INFO, "employee_created", employee_id=7, admin_id=1)
    assert caplog.messages == ["employee_created employee_id=7 admin_id=1"]


@pytest.mark.parametrize("field", ["username", "password", "email", "phone", "first_name", "hash", "cookie"])
def test_personal_or_secret_fields_are_rejected(field: str) -> None:
    with pytest.raises(ValueError):
        format_event("login_failure", **{field: "x"})


@pytest.mark.parametrize("value", ["has space", "a@b.com", "x" * 65, "line\nbreak", ""])
def test_unsafe_values_are_rejected(value: str) -> None:
    with pytest.raises(ValueError):
        format_event("evt", category=value)


def test_unsafe_event_name_rejected() -> None:
    with pytest.raises(ValueError):
        format_event("bad event\nname")


def test_float_and_bool_values_rejected() -> None:
    with pytest.raises(ValueError):
        format_event("evt", count=True)
    with pytest.raises(ValueError):
        format_event("evt", count=1.5)  # type: ignore[arg-type]


def test_server_error_message_excludes_exception_text_but_keeps_traceback(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.ERROR, logger="employee_app"):
        try:
            raise RuntimeError("internal detail")
        except RuntimeError as exc:
            log_server_error("storage_error", exc, category="OperationalError")
    record = caplog.records[0]
    assert record.getMessage() == "storage_error category=OperationalError"
    assert record.exc_info is not None  # stack trace is server-side only


def test_configure_logging_is_idempotent() -> None:
    logger = get_logger()
    saved = list(logger.handlers)
    for handler in saved:
        logger.removeHandler(handler)
    try:
        configure_logging()
        configure_logging()
        assert len(logger.handlers) == 1
    finally:
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
        for handler in saved:
            logger.addHandler(handler)
