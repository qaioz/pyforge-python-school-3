from typing import Annotated
from fastapi import Depends, status, Body, Path, Query, UploadFile, APIRouter
from src.molecules.schema import (
    MoleculeRequest,
    MoleculeResponse,
    SearchParams,
    get_search_params,
    MoleculeCollectionResponse,
)
from src.molecules.service import get_molecule_service
from src.schema import (
    PaginationQueryParams,
    get_pagination_query_params,
    MoleculeUpdateRequest,
    Link,
)
from src.molecules.service import MoleculeService

router = APIRouter()


@router.post(
    "/",
    status_code=201,
    responses={
        # status.HTTP_201_CREATED: {"model": MoleculeResponse},
        status.HTTP_400_BAD_REQUEST: {
            "model": str,
            "description": "Probably due to Invalid SMILES string, or smiles uniqueness violation",
        },
    },
)
def add_molecule(
    molecule_request: Annotated[MoleculeRequest, Body(...)],
    service: Annotated[MoleculeService, Depends(get_molecule_service)],
) -> MoleculeResponse:
    return service.save(molecule_request)


@router.get(
    "/{molecule_id}",
    status_code=200,
    responses={
        # status.HTTP_200_OK: {"model": MoleculeResponse},
        status.HTTP_404_NOT_FOUND: {
            "model": str,
            "description": "Molecule with the given ID not found",
        },
    },
)
def get_molecule(
    molecule_id: Annotated[
        int, Path(..., description="Unique identifier for the molecule")
    ],
    service: Annotated[MoleculeService, Depends(get_molecule_service)],
):
    return service.find_by_id(molecule_id)


@router.get(
    "/",
    status_code=200,
    responses={
        # status.HTTP_200_OK: {"model": list[MoleculeResponse]},
    },
)
def get_molecules(
    service: Annotated[MoleculeService, Depends(get_molecule_service)],
    pagination: Annotated[PaginationQueryParams, Depends(get_pagination_query_params)],
    search_params: Annotated[SearchParams, Depends(get_search_params)],
) -> MoleculeCollectionResponse:
    """
    Get all molecules with pagination and search parameters with pagination support.

    Search by name is a fuzzy search implemented by trigrams.

    You can order the results by mass.

    You can add min_mass and max_mass to filter the results.

    If name is provided, then fuzzy search with trigrams is performed, results are ordered by similarity
    and order_by and order are ignored. Filtering by mass is still possible.

    """

    data = service.find_all(pagination.page, pagination.page_size, search_params)

    return MoleculeCollectionResponse.model_validate(
        {
            "total": len(data),
            "page": pagination.page,
            "page_size": pagination.page_size,
            "data": data,
            "links": {
                "next_page": Link.model_validate(
                    {
                        "href": f"/molecules?page={pagination.page + 1}&pageSize={pagination.page_size}",
                        "rel": "nextPage",
                        "type": "GET",
                    }
                ),
                "prev_page": Link.model_validate(
                    {
                        "href": f"/molecules?page={max(0, pagination.page - 1)}&pageSize={pagination.page_size}",
                        "rel": "prevPage",
                        "type": "GET",
                    }
                ),
            },
        }
    )


@router.patch(
    "/{molecule_id}",
    status_code=200,
    responses={
        # status.HTTP_200_OK: {"model": MoleculeResponse},
        status.HTTP_404_NOT_FOUND: {
            "model": str,
            "description": "Molecule with the given ID not found",
        },
    },
)
def update_molecule(
    molecule_id: Annotated[
        int, Path(..., description="Unique identifier for the molecule")
    ],
    molecule_request: Annotated[MoleculeUpdateRequest, Body(...)],
    service: Annotated[MoleculeService, Depends(get_molecule_service)],
) -> MoleculeResponse:
    """
    Does not really make sense to be able to change the id, smiles, molecular mass of a molecule.
    Only name is allowed to be changed.
    """

    return service.update(molecule_id, molecule_request)


@router.delete(
    "/{molecule_id}",
    status_code=200,
    responses={
        status.HTTP_200_OK: {"description": "Molecule deleted successfully"},
        status.HTTP_404_NOT_FOUND: {
            "model": str,
            "description": "Molecule with the given ID not found",
        },
    },
)
def delete_molecule(
    molecule_id: Annotated[
        int, Path(..., description="Unique identifier for the molecule")
    ],
    service: Annotated[MoleculeService, Depends(get_molecule_service)],
) -> bool:
    return service.delete(molecule_id)


@router.get(
    "/search/substructures",
    responses={
        # status.HTTP_200_OK: {"model": list[MoleculeResponse]},
        status.HTTP_400_BAD_REQUEST: {
            "model": str,
            "description": "Probably due to Invalid SMILES string",
        },
    },
)
def substructure_search(
    smiles: Annotated[
        str,
        Query(
            ...,
            description="Find substructures of the given SMILES string",
        ),
    ],
    service: Annotated[MoleculeService, Depends(get_molecule_service)],
    limit: Annotated[
        int, Query(description="Stop searching after finding this many molecules")
    ] = 1000,
):
    """
    Find all molecules that ARE SUBSTRUCTURES of the given smile, not vice vera.
    """
    return service.get_substructures(smiles, limit)


@router.get(
    "/search/superstructures",
    responses={
        # status.HTTP_200_OK: {"model": list[MoleculeResponse]},
        status.HTTP_400_BAD_REQUEST: {
            "model": str,
            "description": "Probably due to Invalid SMILES string",
        },
    },
)
def substructure_search_of(
    smiles: Annotated[
        str,
        Query(
            ...,
            description="SMILES string that has to be substructure of the found molecules",
        ),
    ],
    service: Annotated[MoleculeService, Depends(get_molecule_service)],
    limit: Annotated[
        int,
        Query(
            description="Stop searching after finding this many molecules",
        ),
    ] = 1000,
):
    """
    Find all molecules that the given smile IS SUBSTRUCTURE OF, not vice vera.
    """
    return service.get_superstructures(smiles, limit)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_molecules(
    file: UploadFile,
    service: Annotated[MoleculeService, Depends(get_molecule_service)],
    validate_rows: Annotated[
        bool,
        Query(
            description="Validate rows before saving, makes slow. False if a 1000 times faster but unsafe"
        ),
    ] = True,
):
    """
    Upload a CSV file containing molecules to the repository.

    The CSV file should have the following columns: smiles,name

    Lines that have incorrect format, missing smiles string or invalid smiles string are ignored.
    """

    # Uploaded CSV file is not stored on the server, only the molecules are extracted and stored in the memory.
    if validate_rows:
        res = service.process_csv_file(file)
    else:
        res = service.bulk_insert_from_file(file)
    return {"number_of_molecules_added": res}
