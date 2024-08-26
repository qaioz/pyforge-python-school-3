from .models.molecule_models import MoleculeInDB
from .schemas.hateoas_schemas import Link
from .schemas.molecule_schemas import AddMoleculeRequest, MoleculeResponse


def molecule_request_to_model(request: AddMoleculeRequest) -> MoleculeInDB:
    return MoleculeInDB(
        smiles=request.smiles,
        molecule_name=request.molecule_name,
        description=request.description,
    )


def molecule_model_to_response(model: MoleculeInDB) -> MoleculeResponse:
    response = MoleculeResponse(
        molecule_id=model.molecule_id,
        smiles=model.smiles,
        molecule_name=model.molecule_name,
        description=model.description,
        links=__generate_links(model.molecule_id),
    )
    return response


def __generate_links(molecule_id: int) -> dict[str, Link]:
    return {
        "self": Link(href=f"/molecules/{molecule_id}", rel="self", type="GET"),
        "substructures": Link(
            href=f"/molecules/{molecule_id}/substructures",
            rel="substructures",
            type="GET",
        ),
    }
