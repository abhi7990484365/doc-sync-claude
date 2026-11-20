"""Plain value object carrying the limits C-4 needs (supplied by the caller)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationLimits:
    name_max_length: int = 100
    email_max_length: int = 254
    max_future_days: int | None = None  # None: no maximum (FR-7 default)
