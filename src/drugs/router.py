from typing import Annotated

from fastapi import APIRouter, Depends, Path, Body
from starlette import status

from src.drugs.schema import DrugResponse, DrugRequest
from src.drugs.service import get_drug_service, DrugService
from src.schema import PaginationQueryParams, get_pagination_query_params

router = APIRouter()


@router.post(
    "/",
    status_code=201,
    responses={
        status.HTTP_201_CREATED: {"model": DrugResponse},
        status.HTTP_400_BAD_REQUEST: {
            "model": str,
            "description": "Probably due to non-exiting reference to molecules",
        },
    },
)
def add_drug(
    drug_request: Annotated[DrugRequest, Body(...)],
    service: Annotated[DrugService, Depends(get_drug_service)],
) -> DrugResponse:
    return service.save(drug_request)


@router.get(
    "/{drug_id}",
    status_code=200,
    responses={
        status.HTTP_200_OK: {"model": list[DrugResponse]},
        status.HTTP_404_NOT_FOUND: {"model": str, "description": "No drugs found"},
    },
)
def get_by_id(
    drug_id: Annotated[int, Path(..., description="Unique identifier for the drug")],
    service: Annotated[get_drug_service, Depends(get_drug_service)],
) -> DrugResponse:
    return service.find_by_id(drug_id)


@router.get(
    "/",
    status_code=200,
    responses={status.HTTP_200_OK: {"model": list[DrugResponse]}},
)
def get_all(
    pagination_args: Annotated[
        PaginationQueryParams, Depends(get_pagination_query_params)
    ],
    service: Annotated[DrugService, Depends(get_drug_service)],
) -> list[DrugResponse]:
    return service.find_all(
        page_size=pagination_args.page_size, page=pagination_args.page
    )


@router.delete(
    "/{drug_id}",
    status_code=200,
    responses={
        status.HTTP_200_OK: {"model": bool},
        status.HTTP_404_NOT_FOUND: {"model": str, "description": "No drugs found"},
    },
)
def delete(
    drug_id: Annotated[int, Path(..., description="Unique identifier for the drug")],
    service: Annotated[DrugService, Depends(get_drug_service)],
) -> bool:
    return service.delete(drug_id)
