from src.molecules.schema import MoleculeResponse, MoleculeRequest
from src.schema import Link
from rdkit import Chem
from rdkit.Chem.Descriptors import MolWt


def generate_links_from_id(molecule_id: int):
    return {
        "self": Link.model_validate(
            {
                "href": f"/molecules/{molecule_id}",
                "rel": "self",
                "type": "GET",
            }
        ),
        "molecules/search/substructures": Link.model_validate(
            {
                "href": f"/molecules/search/substructures?molecule_id={molecule_id}",
                "rel": "substructures",
                "type": "GET",
            }
        ),
        "molecules/search/is_substructure_of": Link.model_validate(
            {
                "href": f"/molecules/search/is_substructure_of?molecule_id={molecule_id}",
                "rel": "substructures",
                "type": "GET",
            }
        ),
    }


def generate_links_from_id_and_smiles(molecule_id: int, smiles: str):
    return {
        "self": Link.model_validate(
            {
                "href": f"/molecules/{molecule_id}",
                "rel": "self",
                "type": "GET",
            }
        ),
        "substructures": Link.model_validate(
            {
                "href": f"/molecules/search/substructures?smiles={smiles}",
                "rel": "substructures",
                "type": "GET",
            }
        ),
        "superstructures": Link.model_validate(
            {
                "href": f"/molecules/search/superstructures?smiles={smiles}",
                "rel": "superstructures",
                "type": "GET",
            }
        ),
    }


def model_to_response(molecule):
    return MoleculeResponse(
        molecule_id=molecule.molecule_id,
        smiles=molecule.smiles,
        name=molecule.name,
        mass=molecule.mass,
        created_at=molecule.created_at.isoformat() if molecule.created_at else None,
        updated_at=molecule.updated_at.isoformat() if molecule.updated_at else None,
        links=generate_links_from_id_and_smiles(molecule.molecule_id, molecule.smiles),
    )


def request_to_model_json(molecule_request: MoleculeRequest) -> dict:
    # calculate molecular mass
    molecule = Chem.MolFromSmiles(molecule_request.smiles)
    mass = MolWt(molecule)
    return {
        "smiles": molecule_request.smiles,
        "name": molecule_request.name,
        "mass": mass,
    }
