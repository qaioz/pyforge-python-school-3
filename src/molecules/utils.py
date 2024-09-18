from collections import OrderedDict
from functools import lru_cache

from rdkit import Chem

from src.molecules.exception import InvalidSmilesException


def is_valid_smiles(smiles: str) -> bool:
    """
    Check if a SMILES string represents a valid molecule.

    :param smiles: SMILES string
    :return: True if the SMILES string not empty and represents a valid molecule , False otherwise
    """
    if not smiles:
        return False
    return Chem.MolFromSmiles(smiles) is not None


def get_chem_molecule_from_smiles_or_raise_exception(smiles: str):
    """
    Get a RDKit molecule object from a SMILES string or raise an InvalidSmilesException.

    :param smiles: SMILES string
    :return: RDKit molecule object
    :raises InvalidSmilesException: if the SMILES string
    """

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise InvalidSmilesException(smiles)
    return mol


class ChemService:
    DEFAULT_CACHE_SIZE = 1000

    def __init__(self, cache_size: int = DEFAULT_CACHE_SIZE):
        self._cache_size = cache_size
        self._cache = OrderedDict()

    def get_chem(self, smiles: str):
        if smiles in self._cache:
            return self._cache[smiles]

        mol = get_chem_molecule_from_smiles_or_raise_exception(smiles)
        if len(self._cache) >= self._cache_size:
            self._cache.popitem(last=False)
        self._cache[smiles] = mol
        return mol


@lru_cache
def get_chem_service():
    return ChemService()
