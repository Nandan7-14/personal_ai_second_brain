import os
import pickle
from typing import Dict, List, Tuple

import faiss
import numpy as np

from utils.helpers import get_database_path


INDEX_PATH = get_database_path("faiss_index.bin")
META_PATH = get_database_path("faiss_meta.pkl")

_index: faiss.IndexFlatL2 | None = None
_meta: List[Dict] = []


def _load_or_create_index(dim: int) -> faiss.IndexFlatL2:
    global _index
    if _index is not None:
        return _index
    if os.path.exists(INDEX_PATH):
        _index = faiss.read_index(INDEX_PATH)
    else:
        _index = faiss.IndexFlatL2(dim)
    return _index


def _load_or_init_meta() -> List[Dict]:
    global _meta
    if _meta:
        return _meta
    if os.path.exists(META_PATH):
        with open(META_PATH, "rb") as f:
            _meta = pickle.load(f)
    else:
        _meta = []
    return _meta


def _persist() -> None:
    if _index is not None:
        faiss.write_index(_index, INDEX_PATH)
    if _meta is not None:
        with open(META_PATH, "wb") as f:
            pickle.dump(_meta, f)


def add_embeddings(embeddings: np.ndarray, chunks: List[str], source: str) -> int:
    """
    Add embeddings and corresponding text chunks into FAISS index + metadata.
    Returns number of chunks added.
    """
    global _meta

    if embeddings.size == 0 or not chunks:
        return 0

    index = _load_or_create_index(embeddings.shape[1])
    index.add(embeddings)

    meta = _load_or_init_meta()
    start_id = len(meta)
    for i, text in enumerate(chunks):
        meta.append(
            {
                "id": start_id + i,
                "source": source,
                "text": text,
            }
        )
    _meta = meta
    _persist()
    return len(chunks)


def search(embedding: np.ndarray, top_k: int = 5) -> List[Tuple[float, Dict]]:
    """
    Perform a similarity search and return (distance, metadata) pairs.
    """
    index = _load_or_create_index(embedding.shape[1])
    meta = _load_or_init_meta()

    if index.ntotal == 0 or not meta:
        return []

    distances, indices = index.search(embedding, min(top_k, index.ntotal))
    results: List[Tuple[float, Dict]] = []
    for dist, idx in zip(distances[0], indices[0]):
        if 0 <= idx < len(meta):
            results.append((float(dist), meta[idx]))
    return results


def build_context(results: List[Tuple[float, Dict]], max_chars: int = 3000) -> str:
    """
    Build a context string from search results, truncated by character budget.
    """
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

