from typing import Annotated
import src.mapper as mapper
from src.dependencies import get_molecule_repository as repository
from fastapi import APIRouter, Body
from fastapi import Depends
from fastapi import status

from src.models.molecule_models import MoleculeInDB
from src.repository.abstract_repository import Repository
from src.schemas.molecule_schemas import AddMoleculeRequest, MoleculeResponse

router = APIRouter()


@router.post("/",
             status_code=status.HTTP_201_CREATED,
             responses={status.HTTP_201_CREATED: {"description": "Molecule added successfully"},
                        status.HTTP_400_BAD_REQUEST: {"description": "Smiles string is invalid or missing"}}
             )
def add_molecule(add_molecule_request: Annotated[AddMoleculeRequest, Body(description="The request body")],
                 molecules_repository: Repository[int] = Depends(repository)) -> MoleculeResponse:
    """
    Add a new molecule to the repository.

    :param add_molecule_request: The request body.

    :param molecules_repository: The repository to add the molecule to.

    :return MoleculeResponse: containing the details of the added molecule.

    :raises InvalidSmilesException:
    """

    print(add_molecule_request.dict())
    molecule = mapper.request_to_model(add_molecule_request)
    molecules_repository.add(molecule)
    return mapper.model_to_response(molecule)

#
# @app.get("/molecules/{molecule_id}",
#          status_code=status.HTTP_200_OK,
#          responses={status.HTTP_200_OK: {"description": "Molecule found successfully"},
#                     status.HTTP_404_NOT_FOUND: {"description": "Molecule with the provided ID is not found"}}
#          )
# def get_molecule(molecule_id: Annotated[int, Path(description="The ID of the molecule")]) -> MoleculeResponse:
#     """
#     Get the details of a molecule by its ID.
#
#     :param molecule_id: The ID of the molecule.
#
#     :return MoleculeResponse: containing the details of the molecule.
#
#     :raises UnknownIdentifierException: If the molecule with the provided ID is not found.
#     """
#
#     if not molecules_repository.exists_by_id(molecule_id):
#         raise exception.UnknownIdentifierException(molecule_id)
#
#     molecule = molecules_repository.find_by_id(molecule_id)
#     return MoleculeResponse.from_molecule(molecule)
#
#
# @app.put("/molecules/{molecule_id}",
#          status_code=status.HTTP_200_OK,
#          responses={status.HTTP_200_OK: {"description": "Molecule updated successfully"},
#                     status.HTTP_404_NOT_FOUND: {"description": "Molecule with the provided ID is not found"}})
# def update_molecule(molecule_id: Annotated[int, Path(description="The ID of the molecule")]
#                     , update_molecule_request: Annotated[AddMoleculeRequest, Body(description="The request body")]
#                     ) -> MoleculeResponse:
#     """
#     Update the details of a molecule by its ID.
#
#     Molecule with the provided ID in the path parameter is overwritten with the details provided in the request body,
#     except for the molecule_id.
#
#     :param molecule_id: The ID of the molecule.
#
#     :param update_molecule_request: The request body.
#
#     :return MoleculeResponse: containing the details of the updated molecule.
#
#     :raises UnknownIdentifierException: If the molecule with the provided ID is not found.
#     """
#
#     if not molecules_repository.exists_by_id(molecule_id):
#         raise exception.UnknownIdentifierException(molecule_id)
#
#     mol = molecules_repository.find_by_id(molecule_id)
#     mol.molecule_name = update_molecule_request.molecule_name
#     mol.smiles = update_molecule_request.smiles
#     mol.description = update_molecule_request.description
#
#     return MoleculeResponse.from_molecule(mol)
#
#
# @app.delete("/molecules/{molecule_id}",
#             status_code=status.HTTP_200_OK,
#             responses={status.HTTP_200_OK: {"description": "Molecule deleted successfully"},
#                        status.HTTP_404_NOT_FOUND: {"description": "Molecule with the provided ID is not found"}})
# def delete_molecule(molecule_id: Annotated[int, Path(description="The ID of the molecule")]) -> None:
#     """
#     Delete a molecule by its ID.
#
#     :param molecule_id:
#
#     :raises HTTPException: If the molecule with the provided ID is not found.
#
#     :return: None
#     """
#
#     if not molecules_repository.exists_by_id(molecule_id):
#         raise exception.UnknownIdentifierException(molecule_id)
#
#     molecules_repository.delete_by_id(molecule_id)
#     return
#
#
# @app.get("/molecules", status_code=status.HTTP_200_OK,
#          responses={status.HTTP_200_OK: {"description": "Molecules found successfully"},
#                     status.HTTP_400_BAD_REQUEST: {"description": "limit has to be greater or equal to skip"}}
#          )
# def list_molecules(skip: Annotated[int, Query(ge=0)] = 0,
#                    limit: Annotated[
#                        int, Query(ge=0, description="If 0, this parameter is ignored. Has to be >= skip")] = 0) \
#         -> list[MoleculeResponse]:
#     """
#     List all molecules in the repository.
#
#     :param skip: offset
#
#     :param limit: number of molecules to return
#
#     :return: list of MoleculeResponse
#
#     :raises HTTPException: If limit is less than skip
#     """
#
#     if limit < skip:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="limit has to be greater or equal to skip")
#
#     find_all = molecules_repository.find_all()
#
#     if limit == 0:
#         limit = len(find_all)
#
#     return [MoleculeResponse.from_molecule(mol) for mol in find_all[skip:skip + limit]]
#
#
# @app.get("/molecules/{molecule_id}/substructures",
#          status_code=status.HTTP_200_OK,
#          responses={status.HTTP_200_OK: {"description": "Molecules found successfully"},
#                     status.HTTP_400_BAD_REQUEST: {"description": "limit has to be greater or equal to skip"}
#                     })
# def get_substructure_search(
#         molecule_id: Annotated[int, Path(description="The ID of the molecule")],
#         skip: Annotated[int, Query(ge=0,description="Offset")] = 0,
#         limit: Annotated[int, Query(ge=0, description="Number of items to return. If 0, this parameter is ignored. "
#                                                       "Has to be >= skip")] = 0,
# ) -> list[MoleculeResponse]:
#     """
#     Find molecules in the that are substructures of given molecule.
#
#     This method will always return at least one molecule, the molecule with the provided ID.
#
#     :param molecule_id:
#
#     :param skip:
#
#     :param limit:
#
#     :return:
#
#     :raises HTTPException: If limit is less than skip
#     """
#
#     if limit < skip:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="limit has to be greater or equal to skip")
#
#     if not molecules_repository.exists_by_id(molecule_id):
#         raise exception.UnknownIdentifierException(molecule_id)
#
#     mol = molecules_repository.find_by_id(molecule_id)
#
#     substructure = Chem.MolFromSmiles(mol.smiles)
#     find_all = molecules_repository.find_all()
#     result_molecules = [m for m in find_all if substructure.HasSubstructMatch(Chem.MolFromSmiles(m.smiles))]
#     if limit == 0:
#         limit = len(result_molecules)
#     responses = [MoleculeResponse.from_molecule(m) for m in result_molecules][skip:skip + limit]
#     return responses
#
#
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
