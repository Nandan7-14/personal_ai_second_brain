# Personal AI Second Brain

This project is a **personal AI assistant** that combines:

- Document memory (RAG over your notes)
- Chat assistant
- Task manager with reminders
- Diary / journal
- Document summarization

It is built with **Streamlit**, **SentenceTransformers**, **FAISS**, **SQLite**, and **APScheduler**.

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

Set your OpenAI API key (PowerShell example):

```powershell
$env:OPENAI_API_KEY = "your_real_key_here"
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

