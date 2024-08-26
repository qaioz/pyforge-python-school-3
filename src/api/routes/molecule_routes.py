from typing import Annotated
import src.exceptions as exception
from fastapi import APIRouter, Body, Path
from fastapi import Depends
from fastapi import status
from src.schemas.molecule_schemas import AddMoleculeRequest, MoleculeResponse
from src.dependencies import get_molecule_repository, get_common_query_parameters
from src.repository.molecule_repositories import AbstractMoleculeRepository
from src.mapper import molecule_model_to_response, molecule_request_to_model
from src.utils import fund_substructures

router = APIRouter()

molecule_repository = Annotated[
    AbstractMoleculeRepository, Depends(get_molecule_repository)
]
query_parameters = Annotated[dict, Depends(get_common_query_parameters)]


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "Molecule added successfully"},
        status.HTTP_400_BAD_REQUEST: {
            "description": "Smiles string is invalid or missing"
        },
    },
)
def add_molecule(
        add_molecule_request: Annotated[
            AddMoleculeRequest, Body(description="The request body")
        ],
        repository: molecule_repository,
) -> MoleculeResponse:
    """
        Add a new molecule to the repository.
    3
        :param add_molecule_request: The request body.

        :return MoleculeResponse: containing the details of the added molecule.

        :raises InvalidSmilesException:
    """

    molecule = molecule_request_to_model(add_molecule_request)
    repository.add(molecule)
    return molecule_model_to_response(molecule)


@router.get(
    "/{molecule_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Molecule found successfully"},
        status.HTTP_404_NOT_FOUND: {
            "description": "Molecule with the provided ID is not found"
        },
    },
)
def get_molecule(
        molecule_id: Annotated[int, Path(description="The ID of the molecule")],
        repository: molecule_repository,
) -> MoleculeResponse:
    """
    Get the details of a molecule by its ID.

    :param molecule_id: The ID of the molecule.

    :return MoleculeResponse: containing the details of the molecule.

    :raises UnknownIdentifierException: If the molecule with the provided ID is not found.
    """

    if not repository.exists_by_id(molecule_id):
        raise exception.UnknownIdentifierException(molecule_id)

    molecule = repository.find_by_id(molecule_id)

    return molecule_model_to_response(molecule)


@router.put(
    "/{molecule_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Molecule updated successfully"},
        status.HTTP_404_NOT_FOUND: {
            "description": "Molecule with the provided ID is not found"
        },
    },
)
def update_molecule(
        molecule_id: Annotated[int, Path(description="The ID of the molecule")],
        update_molecule_request: Annotated[
            AddMoleculeRequest, Body(description="The request body")
        ],
        repository: molecule_repository,
) -> MoleculeResponse:
    """
    Update the details of a molecule by its ID.

    Molecule with the provided ID in the path parameter is overwritten with the details provided in the request body,
    except for the molecule_id.

    :param molecule_id: The ID of the molecule.

    :param update_molecule_request: The request body.

    :return MoleculeResponse: containing the details of the updated molecule.

    :raises UnknownIdentifierException: If the molecule with the provided ID is not found.
    """

    if not repository.exists_by_id(molecule_id):
        raise exception.UnknownIdentifierException(molecule_id)

    mol = repository.find_by_id(molecule_id)
    mol.molecule_name = update_molecule_request.molecule_name
    mol.smiles = update_molecule_request.smiles
    mol.description = update_molecule_request.description

    return molecule_model_to_response(mol)


@router.delete(
    "/{molecule_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Molecule deleted successfully"},
        status.HTTP_404_NOT_FOUND: {
            "description": "Molecule with the provided ID is not found"
        },
    },
)
def delete_molecule(
        molecule_id: Annotated[int, Path(description="The ID of the molecule")],
        repository: molecule_repository,
) -> None:
    """
    Delete a molecule by its ID.

    :param molecule_id:

    :raises UnknownIdentifierException: If the molecule with the provided ID is not found.

    :return: None
    """

    if not repository.exists_by_id(molecule_id):
        raise exception.UnknownIdentifierException(molecule_id)

    repository.delete_by_id(molecule_id)
    return


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Molecules found successfully"},
        status.HTTP_400_BAD_REQUEST: {"description": "limit has to be non-negative"},
    },
)
def list_molecules(
        params: query_parameters, repository: molecule_repository
) -> list[MoleculeResponse]:
    """
    List all molecules in the repository.

    :param params: Skip and limit parameters.

    :return: list of MoleculeResponse

    :raises HTTPException: If limit is less than skip
    """
    limit = params["limit"]
    skip = params["skip"]

    find_all = repository.find_all()

    if limit == 0:
        limit = len(find_all)

    return [molecule_model_to_response(mol) for mol in find_all[skip: skip + limit]]


@router.get(
    "/{molecule_id}/substructures",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"description": "Molecules found successfully"},
        status.HTTP_400_BAD_REQUEST: {"description": "limit has to be non-negative"},
    },
)
def get_substructure_search(
        molecule_id: Annotated[int, Path(description="The ID of the molecule")],
        query_params: query_parameters,
        repository: molecule_repository,
) -> list[MoleculeResponse]:
    """
    Find molecules in the that are substructures of given molecule.

    This method will always return at least one molecule, the molecule with the provided ID.

    :param molecule_id:

    :param skip:

    :param limit:

    :return:

    :raises HTTPException: If limit is less than skip
    """

    if not repository.exists_by_id(molecule_id):
        raise exception.UnknownIdentifierException(molecule_id)

    mol = repository.find_by_id(molecule_id)
    mols = repository.find_all()

    skip = query_params["skip"]
    limit = query_params["limit"]
    if limit == 0:
        limit = len(mols)

    subs = fund_substructures(mol, mols)

    return [molecule_model_to_response(m) for m in subs][skip: skip + limit]

# @app.post("/upload_molecules_csv", status_code=status.HTTP_201_CREATED)
# async def upload_molecules(file: UploadFile):
#     """
#     Upload a CSV file containing molecules to the repository.
#
#     Uploaded CSV file is not stored on the server, only the molecules are extracted and stored in the memory.
#
#     The CSV file should have the following columns: smiles,name,description
#
#     Lines that have incorrect format, missing smiles string or invalid smiles string are ignored.
#
#     :param file:
#
#     :return: A dictionary containing the key: number_of_molecules_added
#
#     :raises HTTPException: If the file is not a CSV file, or does not have the required columns.
#     """
#
#     if file.content_type != "text/csv":
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be a CSV file")
#
#     contents = await file.read()
#
#     csv_data = contents.decode("utf-8")
#     # if the first line is not smiles,name,description raise an exception
#     # this is a very naive check, because more correct way would be to check column names, because
#     # the order of the columns might be different, or there might be more columns
#     # TODO: change this check to a better one
#     if not csv_data.startswith("smiles,name,description"):
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CSV file should have the following "
#                                                                             "columns: smiles,name,description")
#
#     number_of_molecules_added = 0
#
#     csv_reader = csv.DictReader(csv_data.splitlines())
#     for row in csv_reader:
#         try:
#             validate_smiles(row["smiles"])
#             molecule = Molecule(smiles=row["smiles"], molecule_name=row["name"], description=row["description"])
#             molecules_repository.add(molecule)
#             number_of_molecules_added += 1
#         except exception.InvalidSmilesException:
#             # log somewhere. just printing this time, I have not looked into logging in FastAPI yet.
#             print(f"Invalid SMILES string: {row['smiles']}")
#
#     return {"number_of_molecules_added": number_of_molecules_added}
#
#
