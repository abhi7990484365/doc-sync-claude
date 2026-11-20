"""C-8 Clock: the only place that reads the current moment.

Other modules call ``clock.today_local()`` and ``clock.utc_now()`` through the
module so tests can replace them.
"""

from datetime import date, datetime, timezone


def today_local() -> date:
    """Return the server local date ("today", FR-7, OQ-4)."""
    return datetime.now().astimezone().date()


def utc_now() -> datetime:
    """Return the current time as a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)
