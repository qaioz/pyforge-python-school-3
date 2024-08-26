import logging

from src.exceptions import RepositoryItemNotFountException, HTTPClientException
from HTTP_database_client.src.database_client import HTTPDatabaseClient
from abc import ABC, abstractmethod
from src.models.molecule_models import MoleculeInDB


class IDGenerator(ABC):

    @abstractmethod
    def get_next_id(self) -> int:
        pass


class AbstractMoleculeRepository(ABC):

    def __init__(self, id_generator: IDGenerator):
        self._id_generator = id_generator

    @abstractmethod
    def find_by_id(self, obj_id: int) -> MoleculeInDB:
        pass

    @abstractmethod
    def find_all(self) -> list[MoleculeInDB]:
        pass

    @abstractmethod
    def exists_by_id(self, obj_id: int) -> bool:
        pass

    @abstractmethod
    def add(self, obj: MoleculeInDB) -> MoleculeInDB:
        pass

    @abstractmethod
    def delete_by_id(self, obj_id: int) -> None:
        pass

    @abstractmethod
    def size(self) -> int:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


class DefaultMoleculeIDGenerator(IDGenerator):
    def __init__(self):
        self.__next_id = 0

    def get_next_id(self) -> int:
        next_id = self.__next_id
        self.__next_id += 1
        return next_id


class InMemoryMoleculesRepository(AbstractMoleculeRepository):
    def __init__(self, id_generator: IDGenerator = DefaultMoleculeIDGenerator()):
        super().__init__(id_generator)
        self.molecules = {}

    def find_by_id(self, obj_id: int) -> MoleculeInDB:
        """
        :return:  Model object if found, None otherwise.
        """
        if not self.exists_by_id(obj_id):
            raise RepositoryItemNotFountException(obj_id)
        return self.molecules.get(obj_id)

    def find_all(self) -> list[MoleculeInDB]:
        """
        Its important that the insertion order is preserved.
        Inner implementation of dictionary is ordered in that way since Python 3.7+
        """
        return list(self.molecules.values())

    def exists_by_id(self, obj_id: int) -> bool:
        return obj_id in self.molecules

    def add(self, obj: MoleculeInDB) -> MoleculeInDB:
        """
        If the provided molecule has non-None molecule_id, it will be replaced with a new one.
        """
        obj.set_id(self._id_generator.get_next_id())
        self.molecules[obj.get_id()] = obj
        return obj

    def delete_by_id(self, obj_id: int) -> None:
        """
        :raises RepositoryItemNotFountException: If the object with the provided id does not exist.
        """
        if not self.exists_by_id(obj_id):
            raise RepositoryItemNotFountException(obj_id)
        del self.molecules[obj_id]

    def size(self):
        return len(self.molecules)

    def clear(self) -> None:
        self.molecules.clear()


"""
DefaultIdGenerator is very bad because it starts from 0 when the application restarts.
So, lets implement persistent one using HTTP database
"""


class ExternalPersistentIdGenerator(IDGenerator):
    """
    Create the collection in the database with the provided name. That collection will only contain one document,
    of the form {data: {"next_id": 0}, _document_id: xxxxxxxx}
    That document will be read and updated every time get_next_id is called.
    """

    def __init__(self, base_url: str, generator_name: str = "defaultidgenerator"):
        self.__client = HTTPDatabaseClient(base_url)
        self.__base_url = base_url
        self.__generator_name = generator_name

        # initialize the repository by creating the generator_name collection in the database.
        # If the collection already exists it will not be overwritten
        response = self.__client.create_collection(generator_name)
        if response.status not in [201, 400]:
            raise HTTPClientException(response)

        # add the first document to the collection, if it does not exist
        response = self.__client.get_documents(generator_name)
        if response.status != 200:
            raise HTTPClientException(response)

        if len(response.body["documents"]) != 0:
            return

        response = self.__client.add_document(generator_name, {"data": {"next_id": 0}})
        if response.status != 201:
            raise HTTPClientException(response)

    def get_next_id(self) -> int:
        """
        sends two requests to the server, one to get the current next_id and the other to update it.
        """
        response = self.__client.get_documents(self.__generator_name)
        if response.status != 200:
            raise HTTPClientException(response)
        next_id = response.body["documents"][0]["data"]["next_id"]
        response = self.__client.update_document(
            self.__generator_name,
            response.body["documents"][0]["_document_id"],
            {"data": {"next_id": next_id + 1}},
        )
        if response.status != 200:
            raise HTTPClientException(response)
        return next_id


class HTTPMoleculeRepository(AbstractMoleculeRepository):
    def __init__(self, base_url: str, id_generator: IDGenerator = None):
        logging.info(f"trying to connect to {base_url} ")
        if id_generator is None:
            id_generator = ExternalPersistentIdGenerator(base_url)
        super().__init__(id_generator)
        self.__client = HTTPDatabaseClient(base_url)
        self.__base_url = base_url

        # initialize the repository by creating the molecules collection in the database.
        # If the collection already exists it will not be overwritten.
        response = self.__client.create_collection("molecules")

        if response.status not in [201, 400]:
            raise HTTPClientException(response)

    def find_by_id(self, obj_id: int) -> MoleculeInDB:
        if not self.exists_by_id(obj_id):
            raise RepositoryItemNotFountException(obj_id)

        response = self.__client.get_documents(
            "molecules", field="molecule_id", value=obj_id
        )
        if response.status != 200:
            raise HTTPClientException(response.status)

        # our invariant is that molecule_id is unique, assert that invariant
        assert len(response.body["documents"]) <= 1

        document_data = response.body["documents"][0]["data"]

        return MoleculeInDB(**document_data)

    def find_all(self) -> list[MoleculeInDB]:
        response = self.__client.get_documents("molecules")
        if response.status != 200:
            raise HTTPClientException(response.status)

        documents = response.body["documents"]
        return [MoleculeInDB(**document["data"]) for document in documents]

    def exists_by_id(self, obj_id: int) -> bool:
        response = self.__client.get_documents(
            "molecules", field="molecule_id", value=obj_id
        )
        if response.status != 200:
            raise HTTPClientException(response.status)
        return len(response.body["documents"]) > 0

    def add(self, obj: MoleculeInDB) -> MoleculeInDB:
        next_id = self._id_generator.get_next_id()
        obj.set_id(next_id)
        document = obj.dict()
        response = self.__client.add_document("molecules", {"data": document})
        if response.status != 201:
            raise HTTPClientException(response.status)
        return obj

    def delete_by_id(self, obj_id: int) -> None:
        # Let's not use exists_by_id because it will result in one more request to the server
        response = self.__client.get_documents(
            "molecules", field="molecule_id", value=obj_id
        )
        if response.status != 200:
            raise HTTPClientException(response.status)

        if len(response.body["documents"]) == 0:
            raise RepositoryItemNotFountException(obj_id)

        document_id = response.body["documents"][0]["_document_id"]
        response = self.__client.delete_document("molecules", document_id)
        if response.status != 200:
            raise HTTPClientException(response.status)

    def size(self) -> int:
        response = self.__client.get_collection("molecules")
        return response.body["size"]

    def clear(self) -> None:
        response = self.__client.delete_collection("molecules")
        if response.status != 200:
            raise HTTPClientException(response.status)
        response = self.__client.create_collection("molecules")
        if response.status != 201:
            raise HTTPClientException(response.status)
