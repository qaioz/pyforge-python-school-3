from fastapi.testclient import TestClient

import src.main
from src.main import app

client = TestClient(app)

#     add the following sample data  CCO", "c1ccccc1", "CC(=O)O", "CC(=O)Oc1ccccc1C(=O)O

sample_molecules = {
    "ethanol": {
        "smiles": "CCO",
        "molecule_name": "Ethanol",
        "description": "Ethanol is a chemical compound and a simple alcohol."
    },
    "benzene": {
        "smiles": "c1ccccc1",
        "molecule_name": "Benzene",
        "description": "Benzene is an organic chemical compound."
    },
    "acetic_acid": {
        "smiles": "CC(=O)O",
        "molecule_name": "Acetic Acid",
        "description": "Acetic acid is a chemical compound."
    },
    "aspirin": {
        "smiles": "CC(=O)Oc1ccccc1C(=O)O",
        "molecule_name": "Aspirin",
        "description": "Aspirin is in a group of medications called salicylates."
    },
    "carbon": {
        "smiles": "C",
        "molecule_name": "Carbon",
    },
    "octane": {
        "smiles": "CCCCCCCC",
        "molecule_name": "Octane",
        "description": "Octane is a hydrocarbon and an alkane with the chemical formula C8H18."
    },
    "invalid_smiles": {
        "smiles": "invalid_smiles_string",
        "molecule_name": "Invalid",
        "description": "This is an invalid SMILES string."
    },
    "missing_smiles": {
        "molecule_name": "No SMILES",
        "description": "This request is missing the SMILES string."
    }
}


# 3 test cases for the add_molecule endpoint

def test_add_molecule_success():
    request_data = sample_molecules["aspirin"]
    response = client.post("/molecules", json=request_data)
    assert response.status_code == 201

    response_data = response.json()
    assert response_data["smiles"] == request_data["smiles"]
    assert response_data["molecule_name"] == request_data["molecule_name"]
    assert response_data["description"] == request_data["description"]
    assert "molecule_id" in response_data
    assert "links" in response_data


def test_add_molecule_invalid_smiles():
    request_data = sample_molecules["invalid_smiles"]
    response = client.post("/molecules", json=request_data)
    assert response.status_code == 400


def test_add_molecule_missing_smiles():
    request_data = sample_molecules["missing_smiles"]
    response = client.post("/molecules", json=request_data)
    assert response.status_code == 422


# 2 test cases for the get_molecule endpoint

def test_get_molecule_success():
    request_data = sample_molecules["aspirin"]
    add_response = client.post("/molecules", json=request_data)
    assert add_response.status_code == 201

    add_response_data = add_response.json()
    molecule_id = add_response_data["molecule_id"]

    get_response = client.get(add_response_data["links"]["self"]["href"])
    assert get_response.status_code == 200

    get_response_data = get_response.json()
    assert get_response_data["smiles"] == request_data["smiles"]
    assert get_response_data["molecule_name"] == request_data["molecule_name"]
    assert get_response_data["description"] == request_data["description"]
    assert get_response_data["molecule_id"] == molecule_id
    assert "links" in get_response_data


def test_get_molecule_not_found():
    response = client.get("/molecules/69")
    assert response.status_code == 404


# 2 test cases for the update_molecule endpoint


def test_update_molecule_success():
    request_data = sample_molecules["aspirin"]
    add_response = client.post("/molecules", json=request_data)
    assert add_response.status_code == 201

    add_response_data = add_response.json()
    molecule_id = add_response_data["molecule_id"]

    update_request_data = sample_molecules["carbon"]
    update_response = client.put(add_response_data["links"]["self"]["href"], json=update_request_data)
    assert update_response.status_code == 200

    update_response_data = update_response.json()
    assert update_response_data["smiles"] == update_request_data["smiles"]
    assert update_response_data["molecule_name"] == update_request_data["molecule_name"]
    assert update_response_data["molecule_id"] == molecule_id
    assert "links" in update_response_data


def test_update_molecule_not_found():
    update_request_data = sample_molecules["carbon"]
    response = client.put("/molecules/69", json=update_request_data)
    assert response.status_code == 404


# 1 test cases for the delete_molecule endpoint

def test_delete_molecule():
    request_data = sample_molecules["aspirin"]
    add_response = client.post("/molecules", json=request_data)
    assert add_response.status_code == 201

    add_response_data = add_response.json()

    delete_response = client.delete(add_response_data["links"]["self"]["href"])
    assert delete_response.status_code == 200

    get_response = client.get(add_response_data["links"]["self"]["href"])
    assert get_response.status_code == 404


# test cases for the list_molecules endpoint

def test_list_molecules():
    src.main.molecules_repository.clear()

    request_data = sample_molecules["aspirin"]
    add_response = client.post("/molecules", json=request_data)
    assert add_response.status_code == 201

    request_data = sample_molecules["carbon"]
    add_response = client.post("/molecules", json=request_data)
    assert add_response.status_code == 201

    get_response = client.get("/molecules")
    assert get_response.status_code == 200

    get_response_data = get_response.json()
    assert len(get_response_data) == 2
    assert all(mol["molecule_name"] in ["Aspirin", "Carbon"] for mol in get_response_data)


def test_list_molecules_skip3_limit6_only_two_elements_in_db():
    src.main.molecules_repository.clear()

    request_data = sample_molecules["aspirin"]
    add_response = client.post("/molecules", json=request_data)
    assert add_response.status_code == 201

    request_data = sample_molecules["carbon"]
    add_response = client.post("/molecules", json=request_data)
    assert add_response.status_code == 201

    get_response = client.get("/molecules?skip=3&limit=6")
    assert get_response.status_code == 200
    # size of the response should be 0 since there are only 2 elements in the db
    assert len(get_response.json()) == 0


def test_list_molecules_skip1_limit5_only_three_elements_in_db():
    src.main.molecules_repository.clear()

    request_data = sample_molecules["aspirin"]
    add_response = client.post("/molecules", json=request_data)
    assert add_response.status_code == 201

    request_data = sample_molecules["carbon"]
    add_response = client.post("/molecules", json=request_data)
    assert add_response.status_code == 201

    request_data = sample_molecules["ethanol"]
    add_response = client.post("/molecules", json=request_data)
    assert add_response.status_code == 201

    get_response = client.get("/molecules?skip=1&limit=5")
    assert get_response.status_code == 200
    # size of the response should be 2 since there are only 3 elements in the db
    assert len(get_response.json()) == 2


def test_substructure_search():
    src.main.molecules_repository.clear()
    #     upload the first six molecules with the for loop
    responses = []
    for molecule in list(sample_molecules.values())[:6]:
        post_response = client.post("/molecules", json=molecule)
        assert post_response.status_code == 201
        responses.append(post_response.json())

    #     assert that response has all the molecules
    assert len(responses) == 6
    assert all(mol["molecule_name"] in ["Aspirin", "Ethanol", "Benzene", "Acetic Acid", "Carbon", "Octane"] for mol in
               responses)

    #   search for aspirin substructures, which is response idx 3

    get_response = client.get(responses[3]["links"]["substructures"]["href"])
    assert get_response.status_code == 200

    # all the molecules in the response should be the aspirin substructures,except for the octane

    get_response_data = get_response.json()
    #     assert that it includes all the molecules except the octane
    assert len(get_response_data) == 5
    assert all(mol["molecule_name"] != "Octane" for mol in get_response_data)
    assert all(mol["molecule_name"] in ["Aspirin", "Ethanol", "Benzene", "Acetic Acid", "Carbon"]
               for mol in get_response_data)


