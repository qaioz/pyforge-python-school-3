from src.models.molecule_models import MoleculeInDB
from src.schemas.molecule_schemas import AddMoleculeRequest, MoleculeResponse


def request_to_model(request: AddMoleculeRequest) -> MoleculeInDB:
    return MoleculeInDB(smiles=request.smiles, molecule_name=request.molecule_name, description=request.description)


def model_to_response(model: MoleculeInDB) -> MoleculeResponse:
    response = MoleculeResponse(molecule_id=model.molecule_id, smiles=model.smiles, molecule_name=model.molecule_name,
                                description=model.description)
    return response
