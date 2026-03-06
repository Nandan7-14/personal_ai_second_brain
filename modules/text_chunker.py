from typing import List


def chunk_text(text: str, max_words: int = 350, overlap: int = 50) -> List[str]:
    """
    Split long text into overlapping word-based chunks.
    """
    words = text.split()
    if not words:
        return []

    chunks: List[str] = []
    start = 0
    n = len(words)
    while start < n:
        end = min(start + max_words, n)
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        if end == n:
            break
        start = max(0, end - overlap)
    return chunks

