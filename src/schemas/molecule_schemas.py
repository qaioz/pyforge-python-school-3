from pydantic import BaseModel, field_validator
from rdkit import Chem

from src.exceptions import InvalidSmilesException
from src.schemas.hateoas_schemas import HATEOASResponse


class AddMoleculeRequest(BaseModel):
    smiles: str
    molecule_name: str | None = None
    description: str | None = None

    @field_validator("smiles")
    def validate_smiles(cls, smiles: str) -> str:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise InvalidSmilesException(smiles)
        return smiles

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "smiles": "CC(=O)Oc1ccccc1C(=O)O",
                    "molecule_name": "Aspirin",
                    "description": "Aspirin is in a group of medications called salicylates... so on and so forth.",
                }
            ]
        }
    }


class MoleculeResponse(AddMoleculeRequest, HATEOASResponse):
    molecule_id: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "molecule_id": 1,
                    "smiles": "CC(=O)Oc1ccccc1C(=O)O",
                    "molecule_name": "Aspirin",
                    "description": "Aspirin is in a group of medications called salicylates... so on and so forth.",
                }
            ]
        }
    }
