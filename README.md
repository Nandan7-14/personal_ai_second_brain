# Personal AI Second Brain

This project is a **personal AI assistant** that combines:

- Document memory (RAG over your notes)
- Chat assistant
- Task manager with reminders
- Diary / journal
- Document summarization

It is built with **Streamlit**, **SentenceTransformers**, **FAISS**, **SQLite**, and **APScheduler**.

## What MLDL is used? (for viva)

- **Deep Learning model (Embeddings)**: `SentenceTransformer(all-MiniLM-L6-v2)` (Transformer-based model) converts chunks of your notes into **dense vectors (embeddings)**.
- **ML technique (Semantic search)**: FAISS performs **nearest-neighbor similarity search** over embeddings to retrieve the most relevant chunks.
- **RAG (Retrieval Augmented Generation)**: Retrieved chunks are sent as **context** to an LLM to generate the final answer.

The **API key is only for the LLM generation part**. The “MLDL work” in this project is primarily the **Transformer embeddings + FAISS semantic retrieval + RAG pipeline**.

## Project structure

personal_ai_second_brain/ (this folder)

- `app.py` – main Streamlit app
- `uploads/` – uploaded user documents
- `database/` – SQLite database and vector index files
- `modules/` – core logic modules
  - `file_loader.py` – read PDF / TXT / DOCX
  - `text_chunker.py` – split text into chunks
  - `embeddings.py` – text → embedding vectors
  - `vector_store.py` – FAISS vector index + metadata
  - `rag_pipeline.py` – high-level RAG operations
  - `chatbot.py` – LLM interaction helpers
  - `task_manager.py` – task CRUD on SQLite
  - `diary_manager.py` – diary entry CRUD on SQLite
  - `reminder.py` – reminder scheduling utilities
- `utils/`
  - `helpers.py` – small shared helpers
- `requirements.txt` – Python dependencies

## Setup

Create and activate a virtual environment (optional but recommended), then:

```bash
pip install -r requirements.txt
```

### API key setup (safe)

You should **NOT hardcode** the API key in code.

Choose one:

1) **PowerShell (temporary, current terminal only)**:

```powershell
$env:OPENAI_API_KEY = "your_real_key_here"
```

2) **Local `.env` file (recommended for local)**:

Create a file named `.env` in the project root with:

```text
OPENAI_API_KEY=your_real_key_here
```

3) **Streamlit Community Cloud secrets (recommended for deployment)**:

Add to Streamlit secrets:

```toml
OPENAI_API_KEY = "your_real_key_here"
```

## Run the app

From the project folder:

```bash
streamlit run app.py
```

The app will open in your browser with:

- Document upload + indexing
- Chat over your notes (RAG)
- Task manager + deadlines
- Basic reminder highlighting
- Diary / journal
- Document summarization

## RAG transparency (useful for viva)

After you ask a question, open:

- **“Show retrieved chunks (RAG proof)”**

This displays the top retrieved note chunks from FAISS that were used as context for the answer.

## Notes / limitations

- If you have not indexed documents, the assistant cannot answer from notes.
- PDF text extraction quality depends on whether the PDF contains selectable text (scanned PDFs may need OCR).

