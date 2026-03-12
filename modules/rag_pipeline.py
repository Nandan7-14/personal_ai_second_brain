from typing import List, Tuple, Dict, Any

from . import embeddings
from .text_chunker import chunk_text
from .vector_store import add_embeddings, search, build_context
from .chatbot import answer_with_context, summarize_document


def index_texts(texts: List[str], source: str = "uploaded") -> int:
    """
    High-level helper:
    - chunk texts
    - embed chunks
    - add to vector store
    Returns number of chunks added.
    """
    all_chunks: List[str] = []
    for t in texts:
        all_chunks.extend(chunk_text(t))
    if not all_chunks:
        return 0
    embs = embeddings.encode_texts(all_chunks)
    return add_embeddings(embs, all_chunks, source=source)


def semantic_search(question: str, top_k: int = 5) -> Tuple[str, List[Tuple[float, Dict]]]:
    """
    Run semantic search for a question and return:
    - context string
    - raw (distance, metadata) results
    """
    q_emb = embeddings.encode_query(question)
    results = search(q_emb, top_k=top_k)
    context = build_context(results)
    return context, results


def generate_answer(question: str, chat_history: List[dict] | None = None) -> str:
    """
    Full RAG step: semantic search + LLM answer.
    """
    context, _ = semantic_search(question, top_k=5)
    if not context.strip():
        return "I couldn't find relevant information in your indexed documents. Please upload and index your notes first."
    return answer_with_context(question, context, chat_history or [])


def generate_answer_with_sources(
    question: str,
    chat_history: List[dict] | None = None,
    top_k: int = 5,
) -> Dict[str, Any]:
    """
    Full RAG step with transparency:
    returns a dict with answer, context, and retrieved chunks (metadata).
    """
    context, results = semantic_search(question, top_k=top_k)
    if not context.strip():
        return {
            "answer": "I couldn't find relevant information in your indexed documents. Please upload and index your notes first.",
            "context": "",
            "results": [],
        }
    answer = answer_with_context(question, context, chat_history or [])
    return {
        "answer": answer,
        "context": context,
        "results": results,
    }


def summarize_indexed_notes() -> str:
    """
    Pull a broad context from the vector store and summarize it.
    This uses a generic query to retrieve a wide slice of the memory.
    """
    context, _ = semantic_search("overall content of my notes", top_k=20)
    if not context.strip():
        return "No indexed notes found yet. Please upload and index some documents first."
    return summarize_document(context)

