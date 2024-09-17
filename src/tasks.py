from src.celery import celery_app
from src.config import get_settings
from src.database import get_session_factory, get_database_engine
from src.molecules.repository import get_molecule_repository
from src.molecules.service import get_molecule_service

molecule_service = get_molecule_service(
    repository=get_molecule_repository(),
    session_factory=get_session_factory(
        database_engine=get_database_engine(get_settings().database_url),
    ),
)


@celery_app.task
def substructure_search_task(smiles: str, limit: int):
    return molecule_service.get_substructures(smiles, limit).model_dump()


@celery_app.task
def add(x, y):
    return x + y
