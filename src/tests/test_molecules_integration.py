import pytest
from src.repository.molecule_repositories import InMemoryMoleculesRepository
from src.main import app
import src.tests.sample_data as sample_data
from fastapi.testclient import TestClient

"""
This file contains the Integration tests for the Molecule Routes.
"""


# Override the persistence HTTP repository with an in-memory repository.
def override_repository():
    if not hasattr(override_repository, "repository"):
        override_repository.repository = InMemoryMoleculesRepository()
    return override_repository.repository


app.dependency_overrides[override_repository] = override_repository

client = TestClient(app)


@pytest.mark.parametrize("molecule", [sample_data.schema_aspirin(),
                                      sample_data.schema_carbon_no_name_no_description(),
                                      sample_data.schema_methane_no_description_custom_id()])
def test_add_molecule(molecule):
    response = client.post("/molecules/", json=sample_data.schema_aspirin())
    assert response.status_code == 201
    assert response.json() == molecule
