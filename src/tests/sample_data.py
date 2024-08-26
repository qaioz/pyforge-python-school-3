from src.models.molecule_models import MoleculeInDB
from src.schemas.molecule_schemas import AddMoleculeRequest


def molecule_model_aspirin():
    return MoleculeInDB(
        "CC(=O)Oc1ccccc1C(=O)O",
        molecule_name="Aspirin",
        description="Aspirin is in a group of medications called salicylates... so on and so forth.",
    )


def molecule_model_methane_no_name_no_description():
    return MoleculeInDB("C")


def molecule_model_methane_no_description_custom_id():
    return MoleculeInDB("C", molecule_id=999, molecule_name="Methane")


def schema_aspirin():
    return AddMoleculeRequest(
        smiles="CC(=O)Oc1ccccc1C(=O)O",
        molecule_name="Aspirin",
        description="Aspirin so on and so forth.",
    )


def schema_methane_no_name_no_description():
    return AddMoleculeRequest(smiles="C")


def schema_methane_no_description_custom_id():
    return AddMoleculeRequest(smiles="C", molecule_id=999, molecule_name="Methane")


# schema samples for the following molecules: CCO", "c1ccccc1", "CC(=O)O",  "c1ccccc1


def schema_methanol():
    return AddMoleculeRequest(
        smiles="CCO",
        molecule_name="Methanol",
        description="Methanol is the simplest alcohol.",
    )


def schema_benzene():
    return AddMoleculeRequest(
        smiles="c1ccccc1",
        molecule_name="Benzene",
        description="Benzene is an aromatic hydrocarbon.",
    )


def schema_acetic_acid():
    return AddMoleculeRequest(
        smiles="CC(=O)O",
        molecule_name="Acetic Acid",
        description="Acetic acid is a simple carboxylic acid.",
    )


def schema_toluene():
    return AddMoleculeRequest(
        smiles="Cc1ccccc1",
        molecule_name="Toluene",
        description="Toluene is a common solvent.",
    )
