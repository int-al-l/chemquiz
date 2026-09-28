"""SQLAlchemy engine, session factory and declarative base."""

import sqlite3
from collections.abc import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import DATABASE_URL

# check_same_thread is a SQLite-only quirk: FastAPI serves requests from a
# thread pool, and without this SQLite refuses connections reused across
# threads. It is ignored by every other driver.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


@event.listens_for(Engine, "connect")
def _sqlite_wal(dbapi_connection, _record) -> None:
    """Put SQLite files in WAL mode, so readers never wait for the writer.

    Live games are polled every second by every phone while answers are being
    written, possibly from several backend processes sharing the file. Other
    databases are left alone.
    """
    if isinstance(dbapi_connection, sqlite3.Connection):
        dbapi_connection.execute("PRAGMA journal_mode=WAL")


def begin_write(db: Session) -> None:
    """Open this session's transaction as a writer, before it reads.

    A read-check-write sequence (is the question still open? then record the
    answer) is only safe if nobody writes in between. Postgres gets that from
    `SELECT ... FOR UPDATE`, which the caller adds to its query. SQLite has no
    row locks, so the transaction starts with BEGIN IMMEDIATE: one writer for
    the whole file at a time, which is plenty for writes this small.

    Call it before anything else in the transaction has written.
    """
    connection = db.connection()
    if connection.dialect.name != "sqlite":
        return
    raw = connection.connection.dbapi_connection
    if not raw.in_transaction:
        connection.exec_driver_sql("BEGIN IMMEDIATE")


def get_db() -> Iterator[Session]:
    """FastAPI dependency yielding a request-scoped session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
