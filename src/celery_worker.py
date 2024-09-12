from celery import Celery

from src.config import get_settings
from src.database import get_session_factory, get_database_url
from src.molecules.repository import get_molecule_repository
from src.molecules.service import get_molecule_service

BROKER = f"redis://{get_settings().REDIS_HOST}:{get_settings().REDIS_PORT}/0"
BACKEND = BROKER
celery = Celery(
    "tasks", broker=BROKER, backend=BACKEND
)
celery.conf.update(task_track_started=True)

# I could not find a way to dinamically inject the service into the task function
# so I had to create a global variable, assemble it like this
# hope I find a better way to do this, I am sure I will
molecule_service = get_molecule_service(
    repository=get_molecule_repository(),
    session_factory=get_session_factory(database_url=get_database_url()),
)


# I tried to create separate file for tasks, but it did not work, there were problems with imports
# errors were "Received unregistered task of type"
@celery.task
def substructure_search_task(smiles, limit):
    ans = molecule_service.get_substructures(smiles, limit)
    return ans.model_dump()
