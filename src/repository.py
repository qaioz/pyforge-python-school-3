from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from src.models import Molecule


KEY = TypeVar('KEY')
VAL = TypeVar('VAL')


class Repository(ABC, Generic[KEY, VAL]):

    @abstractmethod
    def find_by_id(self, molecule_id: KEY) -> VAL | None:
        pass

    @abstractmethod
    def find_all(self) -> list[VAL]:
        pass

    @abstractmethod
    def exists_by_id(self, obj_id: KEY) -> bool:
        pass

    @abstractmethod
    def add(self, obj: VAL) -> VAL:
        pass

    @abstractmethod
    def delete_by_id(self, obj_id: KEY) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


class InMemoryMoleculesRepository(Repository[int, Molecule]):

    def __init__(self):
        self._molecules: dict[int, Molecule] = {}

    def find_by_id(self, molecule_id: int) -> Molecule | None:
        return self._molecules.get(molecule_id, None)

    # notice that the retured molecules will be in the order of insertion.
    # Since python 3.7, dict maintains insertion order of keys.
    def find_all(self) -> list[Molecule]:
        return list(self._molecules.values())

    def exists_by_id(self, molecule_id: int) -> bool:
        return molecule_id in self._molecules

    def add(self, molecule: Molecule) -> Molecule:
        if self.exists_by_id(molecule.molecule_id):
            raise ValueError(f"Molecule with id {molecule.molecule_id} already exists")
        self._molecules[molecule.molecule_id] = molecule
        return molecule

    def delete_by_id(self, molecule_id: int) -> None:
        if molecule_id in self._molecules:
            del self._molecules[molecule_id]
        else:
            raise ValueError(f"Molecule with id {molecule_id} does not exist")

    def clear(self) -> None:
        self._molecules.clear()

