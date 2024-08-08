from abc import ABC, abstractmethod
from typing import TypeVar, Generic

KEY = TypeVar('KEY')


class IDGenerator(ABC, Generic[KEY]):

    @abstractmethod
    def get_next_id(self) -> KEY:
        pass


class RepositoryItem(ABC, Generic[KEY]):

    @abstractmethod
    def get_id(self) -> KEY:
        pass

    @abstractmethod
    def set_id(self, new_id: KEY) -> None:
        pass


class Repository(ABC, Generic[KEY]):

    def __init__(self, id_generator: IDGenerator[KEY]):
        self._id_generator = id_generator

    @abstractmethod
    def find_by_id(self, obj_id: KEY) -> RepositoryItem[KEY] | None:
        pass

    @abstractmethod
    def find_all(self) -> list[RepositoryItem[KEY]]:
        pass

    @abstractmethod
    def exists_by_id(self, obj_id: KEY) -> bool:
        pass

    @abstractmethod
    def add(self, obj: RepositoryItem[KEY]) -> RepositoryItem[KEY]:
        pass

    @abstractmethod
    def delete_by_id(self, obj_id: KEY) -> None:
        pass

    @abstractmethod
    def size(self) -> int:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass
