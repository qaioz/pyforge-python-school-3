from src.models.molecule_models import MoleculeInDB
from src.schemas.molecule_schemas import AddMoleculeRequest, MoleculeResponse


def molecule_model_aspirin():
    return MoleculeInDB("CC(=O)Oc1ccccc1C(=O)O", molecule_name="Aspirin",
                        description="Aspirin is in a group of medications called salicylates... so on and so forth.")


def molecule_model_carbon_no_name_no_description():
    return MoleculeInDB("c")


def molecule_model_methane_no_description_custom_id():
    return MoleculeInDB("C", molecule_id=999, molecule_name="Methane")


def schema_aspirin():
    return AddMoleculeRequest(smiles="CC(=O)Oc1ccccc1C(=O)O", molecule_name="Aspirin",
                              description="Aspirin so on and so forth.")


def schema_carbon_no_name_no_description():
    return AddMoleculeRequest(smiles="c")


def schema_methane_no_description_custom_id():
    return AddMoleculeRequest(smiles="C", molecule_id=999, molecule_name="Methane")
