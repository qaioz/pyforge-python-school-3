from celery import Celery

from src.config import get_settings

celery_app = Celery(
    "tasks",
    broker=f"redis://{get_settings().BROKER_HOST}:{get_settings().BROKER_PORT}/{get_settings().BROKER_DB}",
    backend=f"redis://{get_settings().BACKEND_HOST}:{get_settings().BACKEND_PORT}/{get_settings().BACKEND_DB}",
)

celery_app.autodiscover_tasks(["src.tasks"])
