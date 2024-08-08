from src.repository.abstract_repository import RepositoryItem


class MoleculeInDB(RepositoryItem[int]):
    def __init__(self, smiles: str, molecule_name: str | None = None, description: str | None = None,
                 molecule_id: int = 0):
        self.molecule_id = molecule_id
        self.smiles = smiles
        self.molecule_name = molecule_name
        self.description = description

    def get_id(self) -> int:
        return self.molecule_id

    def set_id(self, new_id: int) -> None:
        self.molecule_id = new_id
