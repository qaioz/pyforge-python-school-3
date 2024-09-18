import datetime
from functools import lru_cache
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, Field


class Link(BaseModel):
    href: str
    rel: str
    type: str

    # model_config = {
    #     "json_schema_extra": {
    #         "examples": [
    #             {"href": "/molecules/1", "rel": "self", "type": "GET"},
    #             {
    #                 "href": "/substructure_search?smiles=C",
    #                 "rel": "substructures",
    #                 "type": "GET",
    #             },
    #         ]
    #     }
    # }


class BaseResponse(BaseModel):
    links: dict[str, Link] = {}
    created_at: Annotated[
        datetime.datetime, Field(description="Timestamp when the entity was created")
    ] = None
    updated_at: Annotated[
        datetime.datetime, Field(description="Timestamp when the entity was updated")
    ] = None

    # model_config = {
    #     "json_schema_extra": {
    #         "examples": {
    #             "self": {"href": "/molecules/1", "rel": "self", "type": "GET"},
    #             "substructures": {
    #                 "href": "/substructure_search?smiles=C",
    #                 "rel": "substructures",
    #                 "type": "GET",
    #             },
    #         }
    #     }
    # }


class MoleculeUpdateRequest(BaseModel):
    """
    It does not really make sense to be able to change the id, smiles, molecular mass of a molecule,
    so only name is allowed to be changed.
    """

    name: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"name": "MethaneChanged"}],
        }
    }


class PaginationQueryParams(BaseModel):
    """Query parameters for paginated responses. Page is 0-indexed."""

    page: Annotated[int, Query(0, description="Page number", ge=0)] = 0
    page_size: Annotated[
        int, Query(1000, description="Number of items per page", ge=1)
    ] = 1000

    model_config = {"json_schema_extra": {"examples": [{"page": 0, "limit": 1000}]}}


@lru_cache
def get_pagination_query_params(page: int = 0, pageSize: int = 1000):
    return PaginationQueryParams(page=page, page_size=pageSize)
