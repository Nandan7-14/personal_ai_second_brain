from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Tuple, Optional

from .task_manager import get_conn


def create_session(title: Optional[str] = None) -> int:
    if not title:
        title = f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO chat_sessions (title) VALUES (?)", (title,))
        conn.commit()
        return int(cur.lastrowid)


def list_sessions(limit: int = 50) -> List[Tuple[int, str, str]]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, title, created_at
            FROM chat_sessions
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [(int(r[0]), str(r[1]), str(r[2])) for r in cur.fetchall()]


def add_message(session_id: int, role: str, content: str) -> None:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO chat_messages (session_id, role, content)
            VALUES (?, ?, ?)
            """,
            (session_id, role, content),
        )
        conn.commit()


def load_messages(session_id: int) -> List[Dict[str, str]]:
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT role, content
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY id ASC
            """,
            (session_id,),
        )
        rows = cur.fetchall()

    return [{"role": str(role), "content": str(content)} for role, content in rows]

