from datetime import date, datetime, time

import streamlit as st

from modules.file_loader import extract_texts_from_uploads
from modules.rag_pipeline import index_texts, generate_answer, summarize_indexed_notes
from modules.task_manager import init_db, add_task, list_tasks, complete_task
from modules.diary_manager import add_diary_entry, list_diary_entries
from modules.reminder import start_scheduler, get_due_task_ids
from utils.helpers import ensure_directories


st.set_page_config(page_title="Personal AI Second Brain", layout="wide")


@st.cache_resource
def _ensure_background_services():
    ensure_directories()
    init_db()
    start_scheduler()
    return True


def sidebar_task_manager():
    st.sidebar.subheader("Task Manager")

    with st.sidebar.form("add_task_form"):
        desc = st.text_input("Task description")
        col1, col2 = st.columns(2)
        with col1:
            due_date = st.date_input("Due date", value=None)
        with col2:
            due_time = st.time_input("Due time", value=time(23, 59))
        submitted = st.form_submit_button("Add task")
        if submitted and desc.strip():
            due_dt = None
            if isinstance(due_date, date):
                due_dt = datetime.combine(due_date, due_time)
            add_task(desc.strip(), due_dt)
            st.success("Task added.")

    st.sidebar.markdown("---")
    st.sidebar.caption("Pending tasks")

    due_ids = set(get_due_task_ids())
    tasks = list_tasks(include_completed=False)
    for tid, desc, due_str, completed, created_at in tasks:
        label = desc
        if due_str:
            label += f" (due {due_str})"
        if tid in due_ids:
            st.sidebar.warning(label)
        else:
            st.sidebar.write(label)
        if st.sidebar.button("Mark done", key=f"task_{tid}"):
            complete_task(tid)
            st.sidebar.success("Marked as completed.")


def diary_section():
    st.header("Diary / Journal")

    col1, _ = st.columns(2)
    with col1:
        entry_date = st.date_input("Entry date", value=date.today(), key="diary_entry_date")
    content = st.text_area("Write what you studied or want to remember today:")

    if st.button("Save diary entry"):
        if content.strip():
            dt = datetime.combine(entry_date, time(0, 0))
            add_diary_entry(dt, content.strip())
            st.success("Diary entry saved.")
        else:
            st.warning("Please write something before saving.")

    st.markdown("---")
    st.subheader("Past entries")

    col2, col3 = st.columns(2)
    with col2:
        start = st.date_input("From", value=None, key="diary_from")
    with col3:
        end = st.date_input("To", value=None, key="diary_to")

    if st.button("Load entries"):
        start_dt = datetime.combine(start, time(0, 0)) if start else None
        end_dt = datetime.combine(end, time(23, 59)) if end else None
        entries = list_diary_entries(start_dt, end_dt)
        if not entries:
            st.info("No diary entries found for this range.")
        else:
            for eid, edate, text, created_at in entries:
                with st.expander(f"{edate} (created {created_at})"):
                    st.write(text)


def notes_and_chat_section():
    st.header("Documents & Assistant")

    st.subheader("Step 3: Upload study materials")
    uploaded_files = st.file_uploader(
        "Upload PDFs, TXT, or DOCX files",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True,
    )

    if st.button("Process & Index Documents"):
        if not uploaded_files:
            st.warning("Please upload at least one document.")
        else:
            with st.spinner("Extracting text and indexing documents..."):
                texts = extract_texts_from_uploads(uploaded_files)
                chunks_added = index_texts(texts, source="uploaded")
            st.success(f"Indexed {chunks_added} chunks from {len(uploaded_files)} file(s).")

    st.markdown("---")
    st.subheader("Step 9: Chat with your notes")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    question = st.text_input("Ask a question from your notes:")
    if st.button("Ask"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking with your notes..."):
                answer = generate_answer(question, st.session_state["chat_history"])
            st.session_state["chat_history"].append({"role": "user", "content": question})
            st.session_state["chat_history"].append({"role": "assistant", "content": answer})

    if st.session_state.get("chat_history"):
        st.markdown("### Conversation")
        for msg in st.session_state["chat_history"]:
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.markdown(f"**Assistant:** {msg['content']}")

    st.markdown("---")
    st.subheader("Step 13: Summarize your notes")
    if st.button("Summarize indexed notes"):
        with st.spinner("Generating summary from your indexed notes..."):
            summary = summarize_indexed_notes()
        st.markdown("### Summary")
        st.write(summary)


def main():
    _ensure_background_services()

    st.title("Personal AI Second Brain")
    st.caption("ChatGPT + Notion + Reminder app combined as a study assistant.")

    sidebar_task_manager()

    tab1, tab2 = st.tabs(["Assistant & Notes", "Diary / Journal"])
    with tab1:
        notes_and_chat_section()
    with tab2:
        diary_section()


if __name__ == "__main__":
    main()

