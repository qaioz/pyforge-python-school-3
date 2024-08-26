import pytest

from src.dependencies import get_molecule_repository
from src.main import app
import src.tests.sample_data as sample_data
from src.repository.molecule_repositories import InMemoryMoleculesRepository
from fastapi.testclient import TestClient

"""
This file contains the Integration tests for the Molecule Routes.
"""

# Override the persistant repository with the in-memory repository that is cleared after each test Do not forget to
# clear the repository after each test, could not find a way to do it automatically with fixtures or yield
repo = InMemoryMoleculesRepository()


def override_get_molecule_repository():
    return repo


app.dependency_overrides[get_molecule_repository] = override_get_molecule_repository


@pytest.fixture
def test_client() -> TestClient:
    return TestClient(app)


@pytest.mark.parametrize(
    "molecule",
    [
        sample_data.schema_aspirin(),
        sample_data.schema_methane_no_description_custom_id(),
        sample_data.schema_methane_no_description_custom_id(),
    ],
)
def test_add_get_molecule(test_client, molecule):
    request_dict = molecule.dict()
    response = test_client.post("/molecules/", json=request_dict)
    response_dict = dict(response.json())
    assert response.status_code == 201
    assert response_dict.get("smiles", None) == request_dict.get("smiles", None)
    assert response_dict.get("molecule_name", None) == request_dict.get(
        "molecule_name", None
    )
    assert response_dict.get("description", None) == request_dict.get(
        "description", None
    )
    get_request = test_client.get(response_dict["links"]["self"]["href"])
    get_response_dict = dict(get_request.json())
    assert get_request.status_code == 200
    assert get_response_dict.get("smiles", None) == request_dict.get("smiles", None)
    assert get_response_dict.get("molecule_name", None) == request_dict.get(
        "molecule_name", None
    )
    assert get_response_dict.get("description", None) == request_dict.get(
        "description", None
    )
    repo.clear()


def test_add_molecule_invalid_smiles(test_client):
    response = test_client.post(
        "/molecules/",
        json={
            "smiles": "SMOIL",
            "molecule_name": "Aspirin",
            "description": "A common painkiller",
        },
    )
    assert response.status_code == 400
    repo.clear()


def test_get_molecule_not_found(test_client):
    response = test_client.get("/molecules/100")
    assert response.status_code == 404
    repo.clear()


def test_update_get_molecule(test_client):
    response = test_client.post("/molecules/", json=sample_data.schema_aspirin().dict())
    response_dict = dict(response.json())
    assert response.status_code == 201
    update_request = {
        "molecule_name": "Aspirin_Updated",
        "description": "A common painkiller",
        "smiles": "CC(=O)Oc1ccccc1C(=O)O",
    }
    put_response = test_client.put(
        response_dict["links"]["self"]["href"], json=update_request
    )
    assert put_response.status_code == 200
    get_request = test_client.get(response_dict["links"]["self"]["href"])
    get_response_dict = dict(get_request.json())
    assert get_request.status_code == 200
    assert get_response_dict.get("smiles", None) == update_request.get("smiles", None)
    assert get_response_dict.get("molecule_name", None) == update_request.get(
        "molecule_name", None
    )
    assert get_response_dict.get("description", None) == update_request.get(
        "description", None
    )
    repo.clear()


def test_update_molecule_invalid_smiles(test_client):
    response = test_client.post("/molecules/", json=sample_data.schema_aspirin().dict())
    response_dict = dict(response.json())
    assert response.status_code == 201
    update_request = {
        "molecule_name": "Aspirin_Updated",
        "description": "A common painkiller",
        "smiles": "SMOIL",
    }
    put_response = test_client.put(
        response_dict["links"]["self"]["href"], json=update_request
    )
    assert put_response.status_code == 400
    repo.clear()


def test_update_molecule_not_found(test_client):
    update_request = {
        "molecule_name": "Aspirin_Updated",
        "smiles": "CC(=O)Oc1ccccc1C(=O)O",
    }
    put_response = test_client.put("/molecules/100", json=update_request)
    assert put_response.status_code == 404
    repo.clear()


@pytest.mark.parametrize(
    "molecule",
    [
        sample_data.schema_aspirin(),
        sample_data.schema_methane_no_description_custom_id(),
        sample_data.schema_methane_no_description_custom_id(),
    ],
)
def test_delete_get_molecule(test_client, molecule):
    request_dict = molecule.dict()
    response = test_client.post("/molecules/", json=request_dict)
    response_dict = dict(response.json())
    assert response.status_code == 201
    delete_request = test_client.delete(response_dict["links"]["self"]["href"])
    assert delete_request.status_code == 200
    repo.clear()


def test_delete_molecule_not_found(test_client):
    delete_request = test_client.delete("/molecules/100")
    assert delete_request.status_code == 404
    repo.clear()


def test_get_all(test_client):
    mol = sample_data.schema_aspirin()
    #     add this 8 times
    for _ in range(8):
        test_client.post("/molecules/", json=mol.dict())
    response = test_client.get("/molecules/")
    response_body = response.json()
    assert response.status_code == 200
    assert len(response_body) == 8
    # assert that each item in the response has the same smiles as the one we added
    for item in response_body:
        assert item["smiles"] == mol.smiles
    repo.clear()


@pytest.mark.parametrize(
    "skip, limit, expected_count",
    [
        (0, 0, 8),
        (3, 0, 5),
        (3, 3, 3),
        (5, 0, 3),
    ],
)
def test_get_all_pagination(test_client, skip, limit, expected_count):
    repo.clear()
    mol = sample_data.schema_aspirin()
    for _ in range(8):
        test_client.post("/molecules/", json=mol.dict())

    response = test_client.get(f"/molecules/?limit={limit}&skip={skip}")
    response_body = response.json()
    assert response.status_code == 200
    assert len(response_body) == expected_count
    repo.clear()


def test_substructure_search_one_molecule_in_db(test_client):
    mol = sample_data.schema_aspirin()
    post_response = test_client.post("/molecules/", json=mol.dict())
    mol_adress = post_response.json()["links"]["self"]["href"]
    response = test_client.get(f"{mol_adress}/substructures")
    response_body = response.json()
    assert response.status_code == 200
    assert len(response_body) == 1
    assert response_body[0]["smiles"] == mol.smiles
    repo.clear()


def test_substructure_search_no_molecule_in_db(test_client):
    response = test_client.get("/molecules/100/substructures")
    assert response.status_code == 404
    repo.clear()


def test_substructure_search(test_client):
    # this is test from the homework 1 readme file
    aspirin_schema = sample_data.schema_aspirin()
    methanol_schema = sample_data.schema_methanol()
    benzene_schema = sample_data.schema_benzene()
    acetic_acid_schema = sample_data.schema_acetic_acid()
    toluene_schema = sample_data.schema_toluene()

    # post aspirin and remember its substructure address
    post_response = test_client.post("/molecules/", json=aspirin_schema.dict())
    aspirin_substructures = post_response.json()["links"]["substructures"]["href"]
    aspirin_id = post_response.json()["molecule_id"]

    # post the rest of the molecules
    mols = [methanol_schema, benzene_schema, acetic_acid_schema, toluene_schema]
    # remmember the ids of the molecules
    ids_of_mols = [aspirin_id]
    for mol in mols:
        mol_resp = test_client.post("/molecules/", json=mol.dict())
        ids_of_mols.append(mol_resp.json()["molecule_id"])

    # get the substructures of aspirin
    response = test_client.get(aspirin_substructures)

    # check that the response is 200
    assert response.status_code == 200
    # check that the response contains all the molecules
    response_body = response.json()
    # assert that the response contains all the molecules
    for mol in response_body:
        assert mol["molecule_id"] in ids_of_mols
