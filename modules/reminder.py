from datetime import datetime
from typing import List

from apscheduler.schedulers.background import BackgroundScheduler

from .cloud_config import using_cloud_db
from .task_manager import get_due_tasks as sqlite_get_due_tasks
from .pg_task_manager import get_due_tasks as pg_get_due_tasks


_scheduler: BackgroundScheduler | None = None
_due_task_ids: List[int] = []


def _check_due_tasks() -> None:
    global _due_task_ids
    if using_cloud_db():
        tasks = pg_get_due_tasks(datetime.utcnow())
    else:
        tasks = sqlite_get_due_tasks(datetime.utcnow())
    _due_task_ids = [t["id"] for t in tasks]


def start_scheduler(interval_minutes: int = 1) -> BackgroundScheduler:
    """
    Start a background scheduler that periodically checks for due tasks.
    Returns the scheduler instance.
    """
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return _scheduler

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        _check_due_tasks,
        "interval",
        minutes=interval_minutes,
        id="due_task_check",
        replace_existing=True,
    )
    _scheduler.start()
    return _scheduler


def get_due_task_ids() -> List[int]:
    """
    Return the list of task IDs that are currently due, as tracked
    by the background scheduler.
    """
    return list(_due_task_ids)

