"""PostgreSQL connection and query helpers."""
from __future__ import annotations

import contextlib
from typing import Any

import psycopg2
from psycopg2 import extras
from psycopg2.extensions import connection as PgConnection

from config import DB_CONFIG


class DatabaseError(Exception):
    pass


@contextlib.contextmanager
def get_connection():
    conn: PgConnection | None = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        yield conn
        conn.commit()
    except psycopg2.Error as exc:
        if conn is not None:
            conn.rollback()
        raise DatabaseError(str(exc)) from exc
    finally:
        if conn is not None:
            conn.close()


def test_connection() -> str:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database()")
            db_name = cur.fetchone()[0]
            cur.execute(
                """
                SELECT COUNT(*) FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                """
            )
            n_tables = cur.fetchone()[0]
    return f"מחובר לבסיס הנתונים '{db_name}' ({n_tables} טבלאות ב-schema public)"


def get_existing_tables() -> set[str]:
    rows = fetch_all(
        """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """
    )
    return {r[0].lower() for r in rows}


def fetch_all(sql: str, params: tuple | None = None) -> list[tuple]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


def fetch_one(sql: str, params: tuple | None = None) -> tuple | None:
    rows = fetch_all(sql, params)
    return rows[0] if rows else None


def execute(sql: str, params: tuple | None = None) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.rowcount


def fetch_dicts(sql: str, params: tuple | None = None) -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]


def call_function(sql: str, params: tuple | None = None) -> Any:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()[0]


def call_procedure_refcursor(
    proc_name: str,
    args: tuple[Any, ...],
    cursor_name: str = "gui_result_cur",
) -> list[tuple]:
    """CALL procedure with INOUT refcursor and FETCH ALL in one transaction."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            placeholders = ", ".join(["%s"] * len(args))
            if placeholders:
                cur.execute(
                    f"CALL {proc_name}({placeholders}, %s::refcursor)",
                    (*args, cursor_name),
                )
            else:
                cur.execute(
                    f"CALL {proc_name}(%s::refcursor)",
                    (cursor_name,),
                )
            cur.execute(f'FETCH ALL IN "{cursor_name}"')
            return cur.fetchall()


def next_id(table: str, pk_column: str) -> int:
    row = fetch_one(f"SELECT COALESCE(MAX({pk_column}), 0) + 1 FROM {table}")
    return int(row[0]) if row else 1
