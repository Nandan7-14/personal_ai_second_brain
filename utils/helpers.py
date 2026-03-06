import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UPLOAD_DIR = PROJECT_ROOT / "uploads"
DATABASE_DIR = PROJECT_ROOT / "database"


def ensure_directories() -> None:
    """
    Ensure that core directories (uploads, database) exist.
    """
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)


def get_database_path(name: str) -> str:
    """
    Return an absolute path inside the database directory.
    """
    ensure_directories()
    return str(DATABASE_DIR / name)

