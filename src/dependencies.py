from typing import Annotated

from fastapi import HTTPException, Query
from fastapi import status
from .repository.molecule_repositories import (
    AbstractMoleculeRepository,
    HTTPMoleculeRepository,
)
from .config import Config


def get_config() -> Config:
    if not hasattr(get_config, "config"):
        get_config.config = Config()
    return get_config.config


def get_molecule_repository() -> AbstractMoleculeRepository:
    if not hasattr(get_molecule_repository, "repository"):
        get_molecule_repository.repository = HTTPMoleculeRepository(
            get_config().DATABASE_URL
        )
    return get_molecule_repository.repository


def get_common_query_parameters(
    skip: Annotated[
        int,
        Query(
            description="Offset to retrieve molecules in the order of "
            "their insertion"
        ),
    ] = 0,
    limit: Annotated[
        int,
        Query(description="The number of items to return. limit = 0 " "means no limit"),
    ] = 0,
) -> dict:
    if limit < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="limit has to be greater or equal to zero",
        )
    return {"skip": skip, "limit": limit}
