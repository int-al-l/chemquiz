"""Minimal forward migration for SQLite databases made by older versions.

`create_all` adds missing tables but never missing columns. Until the project
adopts Alembic, this adds any column the models declare and the table lacks,
using the column's scalar default. That covers everything this codebase has
needed so far (new nullable or defaulted columns).
"""

from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from .database import Base


def _literal(column) -> str:
    default = column.default.arg if column.default is not None else None
    if callable(default) or default is None:
        return "NULL"
    if isinstance(default, bool):
        return "1" if default else "0"
    if isinstance(default, (int, float)):
        return str(default)
    return "'" + str(default).replace("'", "''") + "'"


def add_missing_columns(engine: Engine) -> list[str]:
    added: list[str] = []
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if table.name not in existing_tables:
                continue
            have = {c["name"] for c in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in have:
                    continue
                coltype = column.type.compile(dialect=engine.dialect)
                conn.execute(text(
                    f'ALTER TABLE "{table.name}" ADD COLUMN "{column.name}" '
                    f"{coltype} DEFAULT {_literal(column)}"
                ))
                added.append(f"{table.name}.{column.name}")
    return added
