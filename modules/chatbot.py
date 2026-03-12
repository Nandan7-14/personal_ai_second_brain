import os
from typing import List, Dict

from openai import OpenAI
from openai import RateLimitError, APIError, APITimeoutError


SYSTEM_PROMPT_RAG = """You are a helpful personal study assistant.
You answer questions strictly based on the provided CONTEXT when possible.
If the context does not contain the answer, say you are not sure instead of guessing.
Use concise explanations and, when helpful, bullet points."""

SYSTEM_PROMPT_SUMMARY = """You are an expert note summarizer.
Produce clear, structured summaries with headings and bullet points.
Focus on key definitions, formulas, and steps."""


def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        try:
            import streamlit as st  # type: ignore

            api_key = st.secrets.get("OPENAI_API_KEY")
        except Exception:
            api_key = None
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Please export it before running the app."
        )
    return OpenAI(api_key=api_key)


def answer_with_context(
    question: str,
    context: str,
    chat_history: List[Dict[str, str]] | None = None,
    model: str = "gpt-4o-mini",
) -> str:
    client = _get_client()
    history = chat_history or []
    messages: List[Dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT_RAG},
        {"role": "system", "content": f"CONTEXT:\n{context}"},
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": question})

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""
    except RateLimitError:
        return (
            "OpenAI rate limit / quota reached for this API key. "
            "Please wait a bit, or enable billing / increase limits on your OpenAI account."
        )
    except (APITimeoutError, APIError):
        return "The LLM service is temporarily unavailable. Please try again in a minute."


def summarize_document(text: str, model: str = "gpt-4o-mini", max_chars: int = 8000) -> str:
    if not text.strip():
        return "No text to summarize."

    client = _get_client()
    short_text = text[:max_chars]
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_SUMMARY},
        {"role": "user", "content": f"Summarize the following document:\n\n{short_text}"},
    ]
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
        )
        return resp.choices[0].message.content or ""
    except RateLimitError:
        return (
            "OpenAI rate limit / quota reached for this API key. "
            "Please wait a bit, or enable billing / increase limits on your OpenAI account."
        )
    except (APITimeoutError, APIError):
        return "The LLM service is temporarily unavailable. Please try again in a minute."

