import json
from fastapi import Depends
from src import exception
from src.models.molecule_models import MoleculeInDB
from src.repository.abstract_repository import Repository, IDGenerator
from HTTP_database_client.src.database_client import HTTPDatabaseClient


class DefaultMoleculeIDGenerator(IDGenerator[int]):
    def __init__(self):
        self.__next_id = 0

    def get_next_id(self) -> int:
        next_id = self.__next_id
        self.__next_id += 1
        return next_id


class InMemoryMoleculesRepository(Repository[int]):
    def __init__(self, id_generator: IDGenerator[int] = DefaultMoleculeIDGenerator()):
        super().__init__(id_generator)
        self.__molecules = {}

    def find_by_id(self, obj_id: int) -> MoleculeInDB | None:
        """
        :return:  Model object if found, None otherwise.
        """
        return self.__molecules.get(obj_id, None)

    def find_all(self) -> list[MoleculeInDB]:
        """
            Its important that the insertion order is preserved.
            Inner implementation of dictionary is ordered in that way since Python 3.7+
        """
        return list(self.__molecules.values())

    def exists_by_id(self, obj_id: int) -> bool:
        return obj_id in self.__molecules

    def add(self, obj: MoleculeInDB) -> MoleculeInDB:
        """
            If the provided molecule has non-None molecule_id, it will be replaced with a new one.
        """
        obj.set_id(self._id_generator.get_next_id())
        self.__molecules[obj.get_id()] = obj
        return obj

    def delete_by_id(self, obj_id: int) -> None:
        """
        :raises RepositoryItemNotFountException: If the object with the provided id does not exist.
        """
        if not self.exists_by_id(obj_id):
            raise exception.RepositoryItemNotFountException(obj_id)
        del self.__molecules[obj_id]

    def size(self):
        return len(self.__molecules)

    def clear(self) -> None:
        self.__molecules.clear()


class HTTPMoleculeRepository(Repository[int]):
    def __init__(self, base_url: str = Depends, id_generator: IDGenerator[int] = DefaultMoleculeIDGenerator()):
        super().__init__(id_generator)
        self.__client = HTTPDatabaseClient(base_url)
        self.__base_url = base_url

        # initialize the repository by creating the molecules collection in the database.
        # If the collection already exists it will not be overwritten.
        response = self.__client.create_collection("molecules")

        if response.status not in [201, 400]:
            raise exception.HTTPClientException(response)

    def find_by_id(self, obj_id: int) -> MoleculeInDB | None:
        pass

    def find_all(self) -> list[MoleculeInDB]:
        response = self.__client.get_documents("molecules")
        if response.status != 200:
            raise exception.HTTPClientException(response)
        documents = json.loads(response.read())
        return [MoleculeInDB(**document) for document in documents]

    def exists_by_id(self, obj_id: int) -> bool:
        pass

    def add(self, obj: MoleculeInDB) -> MoleculeInDB:
        obj.set_id(self._id_generator.get_next_id())
        molecule_document = obj.dict()
        response = self.__client.add_document("molecules", molecule_document)
        if response.status != 200:
            raise exception.HTTPClientException(response)
        return obj

    def delete_by_id(self, obj_id: int) -> None:
        pass

    def size(self) -> int:
        pass

    def clear(self) -> None:
        pass
