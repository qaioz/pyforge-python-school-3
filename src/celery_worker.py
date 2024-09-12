from celery import Celery

from src.database import get_session_factory, get_database_url
from src.molecules.repository import get_molecule_repository
from src.molecules.service import get_molecule_service


celery = Celery(
    "tasks", broker="redis://localhost:6370/0", backend="redis://localhost:6370/0"
)


@celery.task
def substructure_search_task(smiles, limit):
    service = get_molecule_service(
        get_molecule_repository(),
        get_session_factory(get_database_url()),
    )
    ans = service.get_substructures(smiles, limit)
    return ans.model_dump()


# celery.conf.update(task_track_started=True)
