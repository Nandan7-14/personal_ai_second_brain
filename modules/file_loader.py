import io
from typing import List

from docx import Document as DocxDocument
from pypdf import PdfReader


def extract_text_from_file(name: str, data: bytes) -> str:
    """
    Extract text from a single uploaded file based on its extension.
    Supports PDF, TXT, DOCX. Falls back to utf-8 decoding for unknown types.
    """
    lname = name.lower()
    if lname.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    if lname.endswith(".txt"):
        return data.decode("utf-8", errors="ignore")
    if lname.endswith(".docx"):
        doc = DocxDocument(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    return data.decode("utf-8", errors="ignore")


def extract_texts_from_uploads(files) -> List[str]:
    """
    Streamlit-friendly helper that accepts a list of UploadedFile objects
    and returns a list of extracted texts.
    """
    texts: List[str] = []
    for f in files:
        raw = f.read()
        texts.append(extract_text_from_file(f.name, raw))
    return texts

