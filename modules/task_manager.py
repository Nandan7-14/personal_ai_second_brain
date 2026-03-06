import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from utils.helpers import get_database_path


DB_PATH = get_database_path("tasks.db")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
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
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                due_datetime TEXT,
                completed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS diary_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_date TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def add_task(description: str, due: Optional[datetime]) -> None:
    due_str = due.isoformat() if due else None
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (description, due_datetime, completed) VALUES (?, ?, 0)",
            (description, due_str),
        )
        conn.commit()


def list_tasks(include_completed: bool = False) -> List[Tuple]:
    with get_conn() as conn:
        cur = conn.cursor()
        if include_completed:
            cur.execute(
                "SELECT id, description, due_datetime, completed, created_at FROM tasks ORDER BY COALESCE(due_datetime, created_at)"
            )
        else:
            cur.execute(
                "SELECT id, description, due_datetime, completed, created_at FROM tasks WHERE completed = 0 ORDER BY COALESCE(due_datetime, created_at)"
            )
        return cur.fetchall()


def complete_task(task_id: int) -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
        conn.commit()


def get_due_tasks(reference: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """
    Return tasks that are due at or before reference and not completed.
    """
    if reference is None:
        reference = datetime.utcnow()
    ref_str = reference.isoformat()
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, description, due_datetime, completed, created_at
            FROM tasks
            WHERE completed = 0
              AND due_datetime IS NOT NULL
              AND due_datetime <= ?
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
                "id": tid,
                "description": desc,
                "due_datetime": due_str,
                "completed": bool(completed),
                "created_at": created_at,
            }
        )
    return results

