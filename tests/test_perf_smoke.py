"""TASK-047 / NFR-3: informative performance smoke test (not a release gate).

Conditions for "normal operation" are Not Found (OQ-12), so this only times one
submission on the test machine. A failure here must not block release.
"""

import time
from pathlib import Path

import pytest

from tests.web_helpers import post_employee, valid_form

pytestmark = pytest.mark.informative


def test_single_submission_completes_well_within_three_seconds(logged_in) -> None:
    started = time.perf_counter()
    response = post_employee(logged_in, valid_form())
    elapsed = time.perf_counter() - started
    assert response.status_code == 303
    assert elapsed < 3.0, f"submission took {elapsed:.2f}s (informative only)"


def test_operator_notes_exist_and_mark_unknowns_exactly() -> None:
    notes = (Path(__file__).resolve().parents[1] / "docs" / "ops-notes.md").read_text(encoding="utf-8")
    assert "`Not Found`" in notes and "journal_mode=WAL" in notes
    for needle in ("-wal", "-shm", "Backup policy"):
        assert needle in notes
