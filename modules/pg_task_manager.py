import psycopg2
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .cloud_config import get_setting


@contextmanager
def get_conn():
    url = get_setting("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set for Postgres backend.")
    conn = psycopg2.connect(url)
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id BIGSERIAL PRIMARY KEY,
                description TEXT NOT NULL,
                due_datetime TEXT,
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS diary_entries (
                id BIGSERIAL PRIMARY KEY,
                entry_date TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id BIGSERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id BIGSERIAL PRIMARY KEY,
                session_id BIGINT NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
        conn.commit()


def add_task(description: str, due: Optional[datetime]) -> None:
    due_str = due.isoformat() if due else None
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (description, due_datetime, completed) VALUES (%s, %s, FALSE)",
            (description, due_str),
        )
        conn.commit()


def list_tasks(include_completed: bool = False) -> List[Tuple]:
    with get_conn() as conn:
        cur = conn.cursor()
        if include_completed:
            cur.execute(
                """
                SELECT id, description, due_datetime, completed, created_at
                FROM tasks
                ORDER BY COALESCE(due_datetime, created_at::text)
                """
            )
        else:
            cur.execute(
                """
                SELECT id, description, due_datetime, completed, created_at
                FROM tasks
                WHERE completed = FALSE
                ORDER BY COALESCE(due_datetime, created_at::text)
                """
            )
        return cur.fetchall()


def complete_task(task_id: int) -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE tasks SET completed = TRUE WHERE id = %s", (task_id,))
        conn.commit()


def get_due_tasks(reference: Optional[datetime] = None) -> List[Dict[str, Any]]:
    if reference is None:
        reference = datetime.utcnow()
    ref_str = reference.isoformat()
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, description, due_datetime, completed, created_at
            FROM tasks
            WHERE completed = FALSE
              AND due_datetime IS NOT NULL
              AND due_datetime <= %s
            ORDER BY due_datetime
            """,
            (ref_str,),
        )
        rows = cur.fetchall()

    results: List[Dict[str, Any]] = []
    for row in rows:
        tid, desc, due_str, completed, created_at = row
        results.append(
            {
                "id": int(tid),
                "description": desc,
                "due_datetime": due_str,
                "completed": bool(completed),
                "created_at": str(created_at),
            }
        )
    return results

