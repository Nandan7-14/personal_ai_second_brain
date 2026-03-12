import os


def get_setting(name: str) -> str | None:
    """
    Read a setting from environment variables first, then Streamlit secrets.
    Works both locally and on Streamlit Community Cloud.
    """
    value = os.getenv(name)
    if value:
        return value
    try:
        import streamlit as st  # type: ignore

        v = st.secrets.get(name)
        if v:
            return str(v)
    except Exception:
        pass
    return None


def using_cloud_db() -> bool:
    return bool(get_setting("DATABASE_URL"))

