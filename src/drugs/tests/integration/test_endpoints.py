import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient
from src.config import get_test_settings
from src.drugs.repository import DrugRepository
from src.drugs.service import DrugService
from src.main import app
from src.molecules.repository import MoleculeRepository
from src.molecules.service import MoleculeService
from src.drugs.tests import sample_data
from src.database import Base, get_database_url

engine = create_engine(get_test_settings().database_url)

session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
drug_repository = DrugRepository()
drug_service = DrugService(drug_repository, session_factory)

mol_repository = MoleculeRepository()
molecule_service = MoleculeService(mol_repository, session_factory)

test_client = TestClient(app)

app.dependency_overrides[get_database_url] = lambda: get_test_settings().database_url


@pytest.fixture
def init_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    # add caffeine molecule
    molecule_service.save(sample_data.caffeine_request)
    # add water and sugar molecules
    molecule_service.save(sample_data.water_request)
    molecule_service.save(sample_data.sugar_request)
    molecule_service.save(sample_data.ethanol_request)
    yield
    Base.metadata.drop_all(engine)


def test_add_drug_find_by_id(init_db):
    post = test_client.post(
        "/drugs/", content=sample_data.coffe_request.model_dump_json()
    )
    assert post.status_code == 201
    response = post.json()
    assert response["name"] == sample_data.coffe_request.name
    assert response["description"] == sample_data.coffe_request.description
    assert len(response["molecules"]) == 3

    get = test_client.get(f"/drugs/{response['drug_id']}")

    assert get.status_code == 200
    response = get.json()
    assert response["name"] == sample_data.coffe_request.name
    assert response["description"] == sample_data.coffe_request.description
    assert len(response["molecules"]) == 3


def test_add_drug_with_nonexistent_molecule(init_db):
    coffe_request = sample_data.coffe_request.__deepcopy__()
    coffe_request.molecules[0].molecule_id = 10232
    post = test_client.post("/drugs/", content=coffe_request.model_dump_json())
    assert post.status_code == 400


def test_find_by_id_with_nonexistent_id(init_db):
    get = test_client.get("/drugs/1000")
    assert get.status_code == 404


def test_delete(init_db):
    post = test_client.post(
        "/drugs/", content=sample_data.coffe_request.model_dump_json()
    )
    assert post.status_code == 201
    response = post.json()
    drug_id = response["drug_id"]

    delete = test_client.delete(f"/drugs/{drug_id}")
    assert delete.status_code == 200


def test_delete_with_nonexistent_id(init_db):
    delete = test_client.delete("/drugs/1000")
    assert delete.status_code == 404


def test_find_all(init_db):
    post = test_client.post(
        "/drugs/", content=sample_data.coffe_request.model_dump_json()
    )
    assert post.status_code == 201
    post = test_client.post(
        "/drugs/", content=sample_data.drunkenstein.model_dump_json()
    )
    assert post.status_code == 201

    get = test_client.get("/drugs/")
    assert get.status_code == 200
    response = get.json()
    assert len(response) == 2
    assert response[0]["name"] == sample_data.coffe_request.name
    assert response[1]["name"] == sample_data.drunkenstein.name


@pytest.mark.parametrize(
    "page, page_size, expected",
    [
        (1, 1, [sample_data.drunkenstein]),
        (0, 2, [sample_data.coffe_request, sample_data.drunkenstein]),
        (1, 4, [sample_data.sample3]),
        (3, 5, []),
    ],
)
def test_find_all_pagination(page, page_size, expected, init_db):
    all_posts = [
        sample_data.coffe_request,
        sample_data.drunkenstein,
        sample_data.sample1,
        sample_data.sample2,
        sample_data.sample3,
    ]

    for post in all_posts:
        post = test_client.post("/drugs/", content=post.model_dump_json())
        assert post.status_code == 201

    get = test_client.get(f"/drugs/?page={page}&pageSize={page_size}")
    assert get.status_code == 200
    response = get.json()

    for i, drug in enumerate(response):
        assert drug["name"] == expected[i].name
        assert drug["description"] == expected[i].description
        assert len(drug["molecules"]) == len(expected[i].molecules)
