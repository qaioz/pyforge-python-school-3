from rdkit import Chem
from src.exception import InvalidSmilesException


def validate_smiles(smiles: str) -> str:
    """
    Validate the SMILES string. If the SMILES string is invalid, raise an InvalidSmilesException.

    :param smiles: The SMILES string.

    :return: The validated SMILES string.

    :raises InvalidSmilesException: If the SMILES string is invalid or empty.
    """
    if not smiles or Chem.MolFromSmiles(smiles) is None:
        raise InvalidSmilesException(smiles=smiles)
    return smiles
