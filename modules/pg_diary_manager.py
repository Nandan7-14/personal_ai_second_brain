from datetime import datetime
from typing import List, Optional, Tuple

from .pg_task_manager import get_conn


def add_diary_entry(entry_date: datetime, content: str) -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO diary_entries (entry_date, content) VALUES (%s, %s)",
            (entry_date.date().isoformat(), content),
        )
        conn.commit()


def list_diary_entries(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[Tuple]:
    query = "SELECT id, entry_date, content, created_at FROM diary_entries"
    params: list[str] = []
    clauses: list[str] = []
    if start_date is not None:
        clauses.append("entry_date >= %s")
        params.append(start_date.date().isoformat())
    if end_date is not None:
        clauses.append("entry_date <= %s")
        params.append(end_date.date().isoformat())
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY entry_date DESC"

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()

