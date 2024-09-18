from celery import Celery
from src.config import get_settings

BROKER = f"redis://{get_settings().BROKER_HOST}:{get_settings().BROKER_PORT}/{get_settings().BROKER_DB}"
BACKEND = f"redis://{get_settings().BACKEND_HOST}:{get_settings().BACKEND_PORT}/{get_settings().BACKEND_DB}"

celery = Celery("tasks", broker=BROKER, backend=BACKEND)
celery.conf.update(task_track_started=True)

# scan for tasks

celery.autodiscover_tasks(["src.tasks"])
