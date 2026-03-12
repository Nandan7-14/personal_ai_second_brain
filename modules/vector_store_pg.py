from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import psycopg2
from pgvector.psycopg2 import register_vector
from psycopg2.extras import execute_values

from .cloud_config import get_setting


EMBEDDING_DIM = 384  # all-MiniLM-L6-v2


def _get_conn():
    url = get_setting("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set for Postgres vector store.")
    conn = psycopg2.connect(url)
    register_vector(conn)
    return conn


def init_vector_store() -> None:
    conn = _get_conn()
    try:
        cur = conn.cursor()
        # pgvector extension (works on Supabase; if it fails, user must enable it)
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS note_chunks (
                id BIGSERIAL PRIMARY KEY,
                source TEXT,
                text TEXT NOT NULL,
                embedding vector({EMBEDDING_DIM}) NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def add_embeddings(embeddings: np.ndarray, chunks: List[str], source: str) -> int:
    if embeddings.size == 0 or not chunks:
        return 0
    if embeddings.shape[1] != EMBEDDING_DIM:
        raise ValueError(f"Embedding dim mismatch: expected {EMBEDDING_DIM}, got {embeddings.shape[1]}")

    rows = [(source, chunks[i], embeddings[i]) for i in range(len(chunks))]
    conn = _get_conn()
    try:
        cur = conn.cursor()
        execute_values(
            cur,
            "INSERT INTO note_chunks (source, text, embedding) VALUES %s",
            rows,
            template="(%s, %s, %s)",
        )
        conn.commit()
        return len(chunks)
    finally:
        conn.close()


def search(embedding: np.ndarray, top_k: int = 5) -> List[Tuple[float, Dict]]:
    if embedding.shape[1] != EMBEDDING_DIM:
        raise ValueError(f"Embedding dim mismatch: expected {EMBEDDING_DIM}, got {embedding.shape[1]}")

    q = embedding[0]
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, source, text, (embedding <-> %s) AS distance
            FROM note_chunks
            ORDER BY embedding <-> %s
            LIMIT %s
            """,
            (q, q, top_k),
        )
        rows = cur.fetchall()
    finally:
        conn.close()

    results: List[Tuple[float, Dict]] = []
    for rid, source, text, dist in rows:
        results.append(
            (
                float(dist),
                {
                    "id": int(rid),
                    "source": source or "uploaded",
                    "text": text,
                },
            )
        )
    return results


def build_context(results: List[Tuple[float, Dict]], max_chars: int = 3000) -> str:
    parts: List[str] = []
    total = 0
    for _, item in results:
        text = item.get("text", "")
        if not text:
            continue
        if total + len(text) > max_chars:
            break
        parts.append(text)
        total += len(text)
    return "\n\n".join(parts)

