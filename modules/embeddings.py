from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model


def encode_texts(texts: List[str]) -> np.ndarray:
    model = get_model()
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings.astype("float32")


def encode_query(query: str) -> np.ndarray:
    model = get_model()
    emb = model.encode([query], show_progress_bar=False, convert_to_numpy=True)
    return emb.astype("float32")

