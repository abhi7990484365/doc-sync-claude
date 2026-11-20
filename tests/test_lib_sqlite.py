"""TASK-004 characterization tests: SQLAlchemy 2.x and SQLite behaviour.

These tests talk to the libraries directly (not to employee_app) and pin the
behaviour the architecture marks "verify at implementation". Every test uses a
temporary FILE database, never an in-memory one.
"""

import time
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError, OperationalError

KNOWN_VALUE = "known-test-value-xyz"


def make_engine(path: Path, *, timeout: float = 0.3, hide: bool = True, wal: bool = True) -> Engine:
    engine = create_engine(
        f"sqlite:///{path.as_posix()}",
        hide_parameters=hide,
        connect_args={"timeout": timeout, "isolation_level": None},
    )

    @event.listens_for(engine, "connect")
    def _on_connect(dbapi_conn, _record):  # type: ignore[no-untyped-def]
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        if wal:
            cur.execute("PRAGMA journal_mode=WAL")
        cur.close()

    @event.listens_for(engine, "begin")
    def _on_begin(conn):  # type: ignore[no-untyped-def]
        mode = conn.get_execution_options().get("sqlite_begin", "DEFERRED")
        conn.exec_driver_sql(f"BEGIN {mode}")

    return engine


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "lib.sqlite3"
    engine = make_engine(path)
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE t (id INTEGER PRIMARY KEY, v TEXT UNIQUE, n INTEGER DEFAULT 0)"))
        conn.execute(text("INSERT INTO t (id, v) VALUES (1, 'seed')"))
    engine.dispose()
    return path


def test_a_hide_parameters_keeps_values_out_of_exception_text(db_path: Path) -> None:
    hidden = make_engine(db_path, hide=True)
    with pytest.raises(IntegrityError) as caught:
        with hidden.begin() as conn:
            conn.execute(text("INSERT INTO t (v) VALUES (:v)"), {"v": "seed"})
    assert "seed" not in str(caught.value)
    assert "parameters hidden" in str(caught.value)


def test_a_without_hide_parameters_values_are_present(db_path: Path) -> None:
    """Negative control: proves the previous test is meaningful."""
    shown = make_engine(db_path, hide=False)
    with pytest.raises(IntegrityError) as caught:
        with shown.begin() as conn:
            conn.execute(text("INSERT INTO t (v) VALUES (:v)"), {"v": "seed"})
    assert "'seed'" in str(caught.value)


def test_b_begin_immediate_waits_at_begin_then_fails_at_begin(db_path: Path) -> None:
    holder = make_engine(db_path)
    waiter = make_engine(db_path, timeout=0.4)
    with holder.connect().execution_options(sqlite_begin="IMMEDIATE") as held:
        held.begin()
        started = time.monotonic()
        with pytest.raises(OperationalError) as caught:
            with waiter.connect().execution_options(sqlite_begin="IMMEDIATE") as other:
                other.begin()
        elapsed = time.monotonic() - started
        held.rollback()
    assert "locked" in str(caught.value).lower()
    assert elapsed >= 0.3  # it waited for the busy timeout at BEGIN


def test_b_waiting_writer_proceeds_when_holder_finishes_in_time(db_path: Path) -> None:
    import threading

    holder = make_engine(db_path)
    waiter = make_engine(db_path, timeout=3.0)
    ready = threading.Event()

    def hold() -> None:
        with holder.connect().execution_options(sqlite_begin="IMMEDIATE") as c:
            c.begin()
            ready.set()
            time.sleep(0.4)
            c.commit()

    thread = threading.Thread(target=hold)
    thread.start()
    ready.wait(5)
    with waiter.connect().execution_options(sqlite_begin="IMMEDIATE") as other:
        other.begin()
        other.execute(text("INSERT INTO t (v) VALUES ('late')"))
        other.commit()
    thread.join()
    with waiter.connect() as check:
        assert check.execute(text("SELECT COUNT(*) FROM t")).scalar_one() == 2


def test_b_deferred_read_then_write_can_fail_late_under_contention(db_path: Path) -> None:
    """Contrast: a deferred transaction that reads first can fail late. This is
    why the architecture starts write transactions as writes (D-25)."""
    holder = make_engine(db_path)
    late = make_engine(db_path, timeout=0.2)
    with late.connect() as conn:
        conn.begin()
        conn.execute(text("SELECT COUNT(*) FROM t")).scalar_one()
        with holder.begin() as other:
            other.execute(text("UPDATE t SET n = n + 1 WHERE id = 1"))
        # In WAL mode the snapshot is stale: writing now fails immediately.
        with pytest.raises(OperationalError):
            conn.execute(text("UPDATE t SET n = n + 1 WHERE id = 1"))
        conn.rollback()


def test_c_update_matching_no_row_still_takes_the_writer_lock(db_path: Path) -> None:
    """NR-12: observed outcome. An UPDATE that changes no row still starts a
    write transaction and blocks other writers until the transaction ends."""
    first = make_engine(db_path)
    second = make_engine(db_path, timeout=0.2)
    with first.connect() as conn:
        conn.begin()
        result = conn.execute(text("UPDATE t SET n = 1 WHERE id = 999"))
        assert result.rowcount == 0
        with pytest.raises(OperationalError):
            with second.connect().execution_options(sqlite_begin="IMMEDIATE") as other:
                other.begin()
        conn.rollback()


def test_d_wal_mode_is_active_and_readers_coexist_with_a_writer(db_path: Path) -> None:
    writer = make_engine(db_path)
    reader = make_engine(db_path)
    with reader.connect() as r:
        assert r.execute(text("PRAGMA journal_mode")).scalar_one() == "wal"
    with writer.connect().execution_options(sqlite_begin="IMMEDIATE") as w:
        w.begin()
        w.execute(text("INSERT INTO t (v) VALUES ('uncommitted')"))
        with reader.connect() as r:
            r.begin()
            assert r.execute(text("SELECT COUNT(*) FROM t")).scalar_one() == 1
            r.rollback()
        w.rollback()


def test_d_without_wal_journal_mode_is_not_wal(tmp_path: Path) -> None:
    path = tmp_path / "plain.sqlite3"
    engine = make_engine(path, wal=False)
    with engine.connect() as conn:
        assert conn.execute(text("PRAGMA journal_mode")).scalar_one() != "wal"


def test_e_foreign_keys_can_be_enabled(db_path: Path) -> None:
    engine = make_engine(db_path)
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE child (id INTEGER PRIMARY KEY, t_id INTEGER REFERENCES t(id))"))
    with pytest.raises(IntegrityError):
        with engine.begin() as conn:
            conn.execute(text("INSERT INTO child (t_id) VALUES (12345)"))


def test_f_integrity_error_is_distinguishable_by_requery(db_path: Path) -> None:
    first = make_engine(db_path)
    second = make_engine(db_path)
    with first.connect().execution_options(sqlite_begin="IMMEDIATE") as a:
        a.begin()
        a.execute(text("INSERT INTO t (v) VALUES (:v)"), {"v": KNOWN_VALUE})
        a.commit()
    with pytest.raises(IntegrityError):
        with second.begin() as b:
            b.execute(text("INSERT INTO t (v) VALUES (:v)"), {"v": KNOWN_VALUE})
    with second.connect() as c:
        found = c.execute(text("SELECT COUNT(*) FROM t WHERE v = :v"), {"v": KNOWN_VALUE}).scalar_one()
    assert found == 1
