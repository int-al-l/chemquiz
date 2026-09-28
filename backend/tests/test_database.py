"""The SQLite settings the live game relies on when several processes share
one database file."""

from __future__ import annotations

import os
import tempfile
import threading
import time
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import begin_write


@pytest.fixture()
def factory():
    handle, path = tempfile.mkstemp(suffix=".db")
    os.close(handle)
    engine = create_engine(f"sqlite:///{path}", connect_args={"check_same_thread": False})
    with engine.begin() as conn:
        conn.exec_driver_sql("CREATE TABLE counter (n INTEGER)")
        conn.exec_driver_sql("INSERT INTO counter VALUES (0)")
    yield sessionmaker(bind=engine)
    engine.dispose()
    for suffix in ("", "-wal", "-shm"):
        Path(path + suffix).unlink(missing_ok=True)


def test_sqlite_files_use_wal(factory):
    with factory() as db:
        assert db.execute(text("PRAGMA journal_mode")).scalar() == "wal"


def test_writers_take_turns(factory):
    """Read-then-write from many threads at once loses no update."""

    def bump():
        with factory() as db:
            begin_write(db)
            n = db.execute(text("SELECT n FROM counter")).scalar()
            time.sleep(0.01)  # widen the window a lost update would need
            db.execute(text("UPDATE counter SET n = :n"), {"n": n + 1})
            db.commit()

    threads = [threading.Thread(target=bump) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    with factory() as db:
        assert db.execute(text("SELECT n FROM counter")).scalar() == 10
