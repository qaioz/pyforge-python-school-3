import os
import random
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.config import get_settings
from src.database import Base
from src.main import app
from src.molecules.repository import MoleculeRepository
from src.molecules.service import get_molecule_service, MoleculeService
from src.molecules.tests.generate_csv_file import generate_testing_files
from src.molecules.tests.testing_utils import (
    alkane_request_jsons,
    validate_response_dict_for_ith_alkane,
    validate_response_dict_for_alkane,
    heptane_isomer_requests,
    get_imaginary_alkane_requests,
)

# engine = create_engine("postgresql://user:password@localhost:5432/db_test")
engine = create_engine(
    get_settings().TEST_DB_URL,
)
session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
molecule_repository = MoleculeRepository()
molecule_service = MoleculeService(molecule_repository, session_factory, None)

client = TestClient(app)
app.dependency_overrides[get_molecule_service] = lambda: molecule_service


@pytest.fixture
def init_db():
    """
    Create the database schema and add first 100 alkanes to the database.
    """
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    #
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS pg_trgm_on_name_idx ON molecules USING gist (name gist_trgm_ops);"
            )
        )
        conn.commit()

    # yield
    #
    # Base.metadata.drop_all(engine)


def post_consecutive_alkanes(start_number, amount):
    """
    This is helper method to set up the rest of the tests. It posts alkanes from start_number to end_number
    and returns the responses.

    Every response is validated to ensure that the response is correct, so can be used in the rest of the tests
    directly.
    :param start_number: the number of the first alkane to post
    :param amount: the number of alkanes to post, auto-capped so that start_number + amount < 100,
    """
    amount = min(amount, 100 - start_number + 1)
    responses = []
    for i in range(start_number, start_number + amount):
        alkane_request = alkane_request_jsons[i]
        response = client.post("/molecules/", json=alkane_request)
        assert response.status_code == 201
        response_json = response.json()
        assert validate_response_dict_for_ith_alkane(response_json, i)
        responses.append(response_json)
    return responses


def post_heptane_isomers():
    responses = []
    for isomer in heptane_isomer_requests.values():
        response = client.post("/molecules/", json=isomer)
        assert response.status_code == 201
        response_json = response.json()
        responses.append(response_json)
    return responses


@pytest.mark.parametrize("i", [random.randint(1, 99) for _ in range(5)])
def test_save_molecule(i, init_db):
    post_consecutive_alkanes(i, 1)


@pytest.mark.parametrize("i", [random.randint(1, 99) for _ in range(5)])
def test_save_duplicate_smiles(i, init_db):
    res = post_consecutive_alkanes(i, 1)[0]
    duplicate_request = {"name": "Gaiozi", "smiles": res["smiles"]}
    response = client.post("/molecules/", json=duplicate_request)
    assert response.status_code == 400


@pytest.mark.parametrize("i", [random.randint(1, 99) for _ in range(5)])
def test_find_by_id(i, init_db):
    response = post_consecutive_alkanes(i, 1)[0]
    response_id = response["molecule_id"]
    response = client.get(f"/molecules/{response_id}")
    assert response.status_code == 200
    assert validate_response_dict_for_ith_alkane(response.json(), i)


@pytest.mark.parametrize("i", [random.randint(1, 99) for _ in range(5)])
def test_find_by_id_not_found(i, init_db):
    response = post_consecutive_alkanes(i, 1)[0]
    response_id = response["molecule_id"]
    response = client.get(f"/molecules/{response_id + 1}")
    assert response.status_code == 404


@pytest.mark.parametrize("i", [random.randint(1, 10) for _ in range(5)])
def test_update_molecule(i, init_db):
    """
    Update the molecule 2 times, and check that the molecule is updated correctly.
    """
    responses = post_consecutive_alkanes(1, 11)
    update_request1 = {"name": "UpdatedName"}
    update_request2 = {"name": "UpdatedName2"}

    for req in [update_request1, update_request2]:
        response = client.patch(f"/molecules/{responses[i]['molecule_id']}", json=req)
        assert response.status_code == 200
        assert response.json()["name"] == req["name"]
        js = response.json()
        js["name"] = responses[i]["name"]
        assert validate_response_dict_for_alkane(js, responses[i])


@pytest.mark.parametrize("i", [random.randint(1, 10) for _ in range(5)])
def test_update_molecule_not_found(i, init_db):
    post_consecutive_alkanes(1, 11)
    update_request = {"name": "UpdatedName"}
    response = client.patch(f"/molecules/{100000}", json=update_request)
    assert response.status_code == 404


@pytest.mark.parametrize("i", [random.randint(1, 10) for _ in range(5)])
def test_delete_molecule(i, init_db):
    responses = post_consecutive_alkanes(1, 11)
    response = client.delete(f"/molecules/{responses[i]['molecule_id']}")
    assert response.status_code == 200
    response = client.get(f"/molecules/{responses[i]['molecule_id']}")
    assert response.status_code == 404


@pytest.mark.parametrize("i", [random.randint(1, 19) for _ in range(10)])
def test_substructures(i, init_db):
    responses = post_consecutive_alkanes(1, 20)
    response = client.get(
        f"/molecules/search/substructures?smiles={responses[i]['smiles']}"
    )
    assert response.status_code == 200
    response_json = response.json()
    # every alkane up to i should be in the response
    for j in range(1, i + 1):
        assert validate_response_dict_for_ith_alkane(response_json[j], j + 1)


@pytest.mark.parametrize("i", [random.randint(1, 20) for _ in range(10)])
def test_superstructures(i, init_db):
    responses = post_consecutive_alkanes(1, 20)
    response = client.get(
        f"/molecules/search/superstructures?smiles={responses[i - 1]['smiles']}"
    )
    assert response.status_code == 200
    response_json = response.json()
    # every alkane from i should be in the response
    for j in range(i, 20):
        assert validate_response_dict_for_ith_alkane(response_json[j - i], j)


@pytest.fixture
def create_testing_files():
    generate_testing_files()
    yield

    os.remove("alkanes.csv")
    os.remove("invalid_header.csv")
    os.remove("decane_nonane_invalid_smiles.csv")


def test_file_upload(init_db, create_testing_files):
    """
    This tests alkanes.csv file which contains 10 alkanes, starting from methane to decane.

    Since the first 3 alkanes are already in the database, the number of molecules added should be 7.


    """
    post_consecutive_alkanes(1, 3)
    with open("alkanes.csv", "rb") as file:
        response = client.post("/molecules/upload", files={"file": file})
        response_json = response.json()
        assert response.status_code == 201
        assert response_json["number_of_molecules_added"] == 7


def test_file_upload_invalid_header(init_db, create_testing_files):
    """
    This tests invalid_header.csv file which has an invalid header.

    The response should be 400.
    """
    with open("invalid_header.csv", "rb") as file:
        response = client.post("/molecules/upload", files={"file": file})
        assert response.status_code == 400


def test_decane_nonane_invalid_smiles(init_db, create_testing_files):
    """
    This tests decane_nonane_invalid_smiles.csv file which has invalid smiles for decane and nonane.

    Only decane and nonane should not be added to the database, so the number of molecules added should be 5
    """
    post_consecutive_alkanes(1, 3)
    with open("decane_nonane_invalid_smiles.csv", "rb") as file:
        response = client.post("/molecules/upload/", files={"file": file})
        assert response.status_code == 201
        response_json = response.json()
        assert response_json["number_of_molecules_added"] == 5


@pytest.mark.parametrize("page, page_size", [(1, 5), (2, 5), (1, 9), (1, 20)])
def test_find_all(page, page_size, init_db):
    post_consecutive_alkanes(1, 10)
    response = client.get(f"/molecules/?page={page}&page_size={page_size}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) <= page_size
    for i in range(page_size * page, min(page_size * page, 10)):
        assert validate_response_dict_for_ith_alkane(
            data[i - page_size * (page - 1)], i + 1
        )


@pytest.mark.parametrize("_", [_ for _ in range(5)])
# just repeat the test 5 times, test uses randomness
def test_find_all_name_filter(_, init_db):
    alkane_requests = get_imaginary_alkane_requests(5, shuffle=True)

    for alkane in alkane_requests:
        response = client.post("/molecules/", json=alkane)
        assert response.status_code == 201

    i = random.randint(0, 4)
    response = client.get(f"/molecules/?name={alkane_requests[i]['name']}")
    assert response.status_code == 200

    assert response.json()["data"][0]["name"] == alkane_requests[i]["name"]


@pytest.mark.parametrize(
    "min_mass, max_mass, expected_length", [(0, 10, 0), (20, 50, 2), (13, 100, 5)]
)
def test_find_all_name_mass_filter(min_mass, max_mass, expected_length, init_db):
    alkane_requests = get_imaginary_alkane_requests(5, shuffle=True)

    for alkane in alkane_requests:
        response = client.post("/molecules/", json=alkane)
        assert response.status_code == 201

    response = client.get(
        f"/molecules/?name={'gaozane'}&minMass={min_mass}&maxMass={max_mass}"
    )

    assert response.status_code == 200

    body = response.json()["data"]
    assert len(body) == expected_length

    for r in body:
        assert min_mass <= r["mass"] <= max_mass


@pytest.mark.parametrize(
    "order,min_mass,max_mass",
    [
        ("asc", None, 100),
        ("desc", 60, None),
        ("asc", 10, 50),
        (None, 10, 50),
        (None, None, 50),
        ("desc", None, 69),
        (None, 69, None),
        ("asc", 10, 100),
    ],
)
def test_order_by_mass_mass_filters(order, min_mass, max_mass, init_db):

    alkane_requests = get_imaginary_alkane_requests(5, shuffle=True)

    for alkane in alkane_requests:
        response = client.post("/molecules/", json=alkane)
        assert response.status_code == 201

    query_builder = "/molecules/?orderBy=mass&"
    if order:
        query_builder += f"order={order}&"
    if min_mass:
        query_builder += f"minMass={min_mass}&"
    if max_mass:
        query_builder += f"maxMass={max_mass}&"

    response = client.get(query_builder)

    min_mass = min_mass if min_mass else 0
    max_mass = max_mass if max_mass else 10**5

    assert response.status_code == 200

    body = response.json()["data"]
    order = order if order else "asc"

    if order == "asc":
        for i in range(len(body) - 1):
            assert body[i]["mass"] <= body[i + 1]["mass"]
            assert min_mass <= body[i]["mass"] <= max_mass
    elif order == "desc":
        for i in range(len(body) - 1):
            assert body[i]["mass"] >= body[i + 1]["mass"]
            assert min_mass <= body[i]["mass"] <= max_mass


def test_find_all_pagination(init_db):
    post_consecutive_alkanes(1, 7)
    response = client.get("/molecules/?page=0&pageSize=5")
    assert response.status_code == 200
    response_body = response.json()

    assert response_body["page"] == 0
    assert response_body["page_size"] == 5
    assert response_body["total"] == 5

    response = client.get(response_body["links"]["next_page"]["href"])
    assert response.status_code == 200

    response_body = response.json()

    assert response_body["page"] == 1
    assert response_body["page_size"] == 5
    assert response_body["total"] == 2
    assert len(response_body["data"]) == 2

    response = client.get(response_body["links"]["prev_page"]["href"])
    assert response.status_code == 200

    response_body = response.json()

    assert response_body["page"] == 0
    assert response_body["page_size"] == 5
    assert response_body["total"] == 5
    assert len(response_body["data"]) == 5

    response = client.get(response_body["links"]["prev_page"]["href"])

    assert response.status_code == 200

    response_body = response.json()

    assert response_body["page"] == 0
    assert response_body["page_size"] == 5
    assert response_body["total"] == 5
    assert len(response_body["data"]) == 5
