import csv
import io
import logging
from functools import lru_cache
from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError

from src.exception import UnknownIdentifierException
from src.molecules.exception import (
    DuplicateSmilesException,
    InvalidCsvHeaderColumnsException,
    InvalidSmilesException,
)
from src.molecules.repository import (
    MoleculeRepository,
    get_molecule_repository,
)
from src.molecules.schema import (
    MoleculeRequest,
    MoleculeResponse,
    SearchParams,
    get_search_params, MoleculeCollectionResponse,
)
from src.molecules.utils import (
    get_chem_molecule_from_smiles_or_raise_exception,
    is_valid_smiles,
    get_chem_service,
)
from src.database import get_session_factory
from src.molecules import mapper
from src.redis import RedisCacheService, get_redis_cache_service
from src.schema import MoleculeUpdateRequest, Link

logger = logging.getLogger(__name__)


class MoleculeService:
    required_columns = {"smiles", "name"}

    def __init__(
            self,
            repository: MoleculeRepository,
            session_factory,
            redis_cache_service: RedisCacheService,
    ):
        self._repository = repository
        self._session_factory = session_factory
        self._redis = redis_cache_service

    def find_by_id(self, obj_id: int):
        """
        Find a molecule by its id. Calls exists_by_id to check if the molecule exists, resulting in two database calls.
        Not vert impressive, but I am trying to keep it simple.

        :param obj_id:  molecule id
        :return: found molecule
        :raises UnknownIdentifierException: if the molecule with the given id does not exist
        """
        with self._session_factory() as session:
            mol = self._repository.find_by_id(obj_id, session)
            if mol is None:
                raise UnknownIdentifierException(obj_id)
            return mapper.model_to_response(mol)

    def save(self, molecule_request: MoleculeRequest):
        """
        Save a new molecule to the database. If the smiles is not unique,
        the database will raise an exception, which is caught and re-raised
        as a DuplicateSmilesException.

        :param molecule_request: Molecule data
        :return: Saved molecule
        """
        with self._session_factory() as session:
            # previous implementation was using filter to check for smiles duplicates, that was not efficient
            # I have removed the filter method from the repository, and I am relying on the IntegrityError,
            # Think this will work just fine.
            try:
                mol_json = mapper.request_to_model_json(molecule_request)
                mol = self._repository.save(session, mol_json)
                session.flush()  # This will trigger the IntegrityError if the smiles is not unique
                session.commit()
                return mapper.model_to_response(mol)
            except IntegrityError as e:
                session.rollback()  # Rollback in case of error
                if "unique constraint" in str(e).lower():
                    raise DuplicateSmilesException(molecule_request.smiles) from e
                raise

    def update(self, obj_id: int, molecule_request: MoleculeUpdateRequest):
        """
        Update a molecule with the given id.
        This is suitable for put request

        :param obj_id: Identifier of the molecule to be updated
        :param molecule_request: New data for the molecule
        :return: Updated molecule
        :raises UnknownIdentifierException: if the molecule with the given id does not exist
        """
        with self._session_factory() as session:
            mol = self._repository.find_by_id(obj_id, session)
            if mol is None:
                raise UnknownIdentifierException(obj_id)

            mol.name = molecule_request.name
            session.commit()
            ans = mapper.model_to_response(mol)
            return ans

    def find_all(
            self, page: int = 0, page_size: int = 1000, search_params: SearchParams = None
    ):
        """
        Find all molecules in the database. Can be paginated. Default page size is 1000.

        :param search_params: Search parameters
        :param page: Zero indexed page number, default is 0
        :param page_size: Items per page, default is 1000
        :return: List of all molecules
        """

        key = self._redis_key("find_all", page=page, page_size=page_size, **search_params.model_dump())
        cached = self._redis.get_json(key)
        if cached:
            logger.info(f"Cache hit for key: {key}")
            return MoleculeCollectionResponse.model_validate(cached)

        logger.info(f"Cache miss for key: {key}")

        with self._session_factory() as session:
            molecules = self._repository.find_all(
                session, page, page_size, search_params
            )

            data = [mapper.model_to_response(mol) for mol in molecules]

            res = MoleculeCollectionResponse.model_validate(
                {
                    "total": len(data),
                    "page": page,
                    "page_size": page_size,
                    "data": data,
                    "links": {
                        "next_page": Link.model_validate(
                            {
                                "href": f"/molecules?page={page + 1}&pageSize={page_size}",
                                "rel": "nextPage",
                                "type": "GET",
                            }
                        ),
                        "prev_page": Link.model_validate(
                            {
                                "href": f"/molecules?page={max(0, page - 1)}&pageSize={page_size}",
                                "rel": "prevPage",
                                "type": "GET",
                            }
                        ),
                    },
                }
            )

            mod = res.model_dump()

            for mol in mod["data"]:
                mol["created_at"] = mol["created_at"].isoformat()
                mol["updated_at"] = mol["updated_at"].isoformat()

            self._redis.set_json(key, mod)

            return res

    def delete(self, obj_id: int) -> bool:
        """
        Delete a molecule with the given id. If the molecule does not exist, raise an exception.

        :param obj_id: Identifier of the molecule to be deleted
        :return: True
        :raises UnknownIdentifierException: if the molecule with the given id does not exist
        """
        with self._session_factory() as session:
            mol = self._repository.find_by_id(obj_id, session)
            if mol is None:
                raise UnknownIdentifierException(obj_id)
            ans = self._repository.delete(session, obj_id)
            session.commit()
            return ans

    def get_substructures(
            self, smiles: str, limit: int = 1000
    ) -> list[MoleculeResponse]:
        """
        Find all molecules that are substructures of the given smiles.

        :param limit:
        :param smiles: smiles string
        :return: List of molecules that are substructures of the given smiles
        :raises InvalidSmilesException: if the smiles does not represent a valid molecule
        """

        mol = get_chem_molecule_from_smiles_or_raise_exception(smiles)
        find_all = self.__iterate_on_find_all()
        count = 0

        for molecule in find_all:
            if mol.HasSubstructMatch(get_chem_service().get_chem(molecule.smiles)):
                yield mapper.model_to_response(molecule)
                count += 1
                if limit is not None and count >= limit:
                    break

    def get_superstructures(
            self, smiles: str, limit: int = 1000
    ) -> list[MoleculeResponse]:
        """
        Find all the molecules that this molecule is a substructure of.

        :param limit: stop searching after finding this many molecules
        :param smiles:
        :return:  List of molecules that this molecule is a substructure of.
        :raises InvalidSmilesException: if the smiles does not represent a valid molecule
        """

        mol = get_chem_molecule_from_smiles_or_raise_exception(smiles)
        find_all = self.__iterate_on_find_all()
        count = 0

        for molecule in find_all:
            if get_chem_service().get_chem(molecule.smiles).HasSubstructMatch(mol):
                yield mapper.model_to_response(molecule)
                count += 1
                if limit is not None and count >= limit:
                    break

    def process_csv_file(self, file: UploadFile):
        """
        Process a CSV file and add molecules to the database. The CSV file must have the following columns:

        - smiles
        - name

        Lines that have incorrect format, missing smiles string or invalid smiles string are ignored, and the valid
        molecules are added to the database.

        :return: Number of molecules added successfully
        """

        csv_reader = csv.DictReader(io.TextIOWrapper(file.file, encoding="utf-8"))

        self.__validate_csv_header_columns(set(csv_reader.fieldnames))

        number_of_molecules_added = 0

        for row in csv_reader:
            try:
                if not is_valid_smiles(row["smiles"]):
                    raise InvalidSmilesException(row["smiles"])
                self.save(MoleculeRequest(smiles=row["smiles"], name=row["name"]))
                number_of_molecules_added += 1
            except InvalidSmilesException as e:
                """
                We are ignoring the exception and continuing to the next line. It is not important
                whole file to be valid, we just want to add as many molecules as possible.
                """
                logger.warning(
                    f"Encountered invalid SMILES string: {e.smiles} in row: {row}"
                )
            except DuplicateSmilesException as e:
                logger.warning(f"Duplicate SMILES string: {e.smiles} in row: {row}")
            except Exception as e:
                logger.error(f"Error processing row: {row}, error: {e}")

        return number_of_molecules_added

    def bulk_insert_from_file(self, file: UploadFile):
        """
        Bulk insert molecules from a CSV file. Similar to process_csv_file, but no rows are
        validated and there is no

        //TODO this method is written in a rush, I will test adn revise many things, but works
        :param file:
        :return:
        """

        csv_reader = csv.DictReader(io.TextIOWrapper(file.file, encoding="utf-8"))
        self.__validate_csv_header_columns(set(csv_reader.fieldnames))
        molecules = []
        added_molecules = 0
        for row in csv_reader:
            molecules.append({"smiles": row["smiles"], "name": row["name"]})
            if len(molecules) == 500:
                with self._session_factory() as session:
                    res = self._repository.bulk_insert(session, molecules)
                    session.commit()
                    added_molecules += res
                    molecules = []
        with self._session_factory() as session:
            res = self._repository.bulk_insert(session, molecules)
            session.commit()
            added_molecules += res
        return added_molecules

    def __validate_csv_header_columns(self, columns: set[str]):
        """
        :param columns:
        :return:
        :raises InvalidCsvHeaderColumnsException:
        """
        missing_columns = self.required_columns - columns
        if missing_columns:
            raise InvalidCsvHeaderColumnsException(missing_columns)

    def __iterate_on_find_all(self, page_size: int = 100):
        """
        This is a helper method that will be used in substructure search methods, or other search methods implemented
        int the future.

        I will implement a simple iterator that will fetch
        chunks of data from the at a time, not to fetch everything entirely.

        Chunk size is defined by page_size. This value is purely implementation detail, could be
        relevant when planning for performance. At this point, I thought it would
        be too much if I move it to the settings or some global attribute.

        :param page_size: Number of items to fetch at a time, default is 100
        """

        with self._session_factory() as session:
            page = 0
            while True:
                chunk = self._repository.find_all(
                    session=session,
                    page=page,
                    page_size=page_size,
                    search_params=get_search_params(),
                )
                if not chunk:
                    break
                for molecule in chunk:
                    yield molecule
                page += 1

    @staticmethod
    def _redis_key(path, **kwargs):
        # sorted args, filter out None values
        sorted_args = sorted([(k, v) for k, v in kwargs.items() if v is not None])
        return f"molecules:{path}:" + ":".join([f"{v}" for k, v in sorted_args])


@lru_cache
def get_molecule_service():
    return MoleculeService(get_molecule_repository(), get_session_factory(), get_redis_cache_service())
