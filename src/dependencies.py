import src.repository.molecule_repositories as molecule_repositories
import src.repository.abstract_repository as abstract_repository
from src import config


# singleton config
def get_config() -> config.Config:
    if not hasattr(get_config, "config"):
        get_config.config = config.Config()
    return get_config.config


# singleton molecule repository
def get_molecule_repository() -> abstract_repository.Repository[int]:
    if not hasattr(get_molecule_repository, "repository"):
        get_molecule_repository.repository = molecule_repositories.InMemoryMoleculesRepository()
    return get_molecule_repository.repository
