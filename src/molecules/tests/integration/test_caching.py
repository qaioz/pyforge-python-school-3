import random
import pytest
import unittest.mock as mock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.config import get_settings
from src.database import Base
from src.main import app
from src.molecules.repository import MoleculeRepository
from src.molecules.schema import MoleculeRequest
from src.molecules.service import get_molecule_service, MoleculeService
from src.molecules.tests.testing_utils import (
    alkane_request_jsons,
    validate_response_dict_for_ith_alkane,
)
from src.redis import get_redis_client, get_redis_cache_service
from src.molecules.tests.testing_utils_for_caching import (
    assert_set_json_called_with_url,
    assert_key_exists_in_cache,
    get_key_from_url_queries,
)

engine = create_engine(
    get_settings().TEST_DB_URL,
)
session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
molecule_repository = MoleculeRepository()

client = TestClient(app)
redis_test_client = get_redis_client()
redis = get_redis_cache_service()

molecule_service = MoleculeService(molecule_repository, session_factory)

app.dependency_overrides[get_molecule_service] = lambda: molecule_service


@pytest.fixture
def init_db():
    """
    Create the database schema and add first 100 alkanes to the database.

    Also delete all keys from the test Redis database.
    """

    redis_test_client.flushdb()
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

    for i in range(1, 11):
        molecule_service.save(MoleculeRequest.model_validate(alkane_request_jsons[i]))
    yield
    redis_test_client.flushdb()


@pytest.mark.parametrize("idx", [random.randint(1, 10) for _ in range(5)])
def test_get_molecule_by_id_mock(idx, init_db):
    """
    Test the GET /molecules/{molecule_id} endpoint.
    """

    # This is the first request, there is no cache and the set_json method should be called
    assert_set_json_called_with_url(
        client, redis, url=f"/molecules/{idx}", should_be_called=True
    )

    # now make a request to the same endpoint, that actually caches the data
    request = client.get(f"/molecules/{idx}")
    assert request.status_code == 200

    # The set_json method should not be called because the cache is already set
    assert_set_json_called_with_url(
        client, redis, url=f"/molecules/{idx}", should_be_called=False
    )


@pytest.mark.parametrize("idx", [random.randint(1, 10) for _ in range(5)])
def test_get_molecule_by_id(idx, init_db):
    # Initially the cache should not have the key
    assert_key_exists_in_cache(redis, f"/molecules/{idx}", should_exist=False)

    # make a request to the endpoint
    request = client.get(f"/molecules/{idx}")
    assert request.status_code == 200
    assert validate_response_dict_for_ith_alkane(request.json(), idx)

    # This should have triggered the set_json method and the cache should be set
    assert_key_exists_in_cache(redis, f"/molecules/{idx}", should_exist=True)

    # Now make the same request again, this time the cache should be hit
    request = client.get(f"/molecules/{idx}")
    assert request.status_code == 200
    assert validate_response_dict_for_ith_alkane(request.json(), idx)


# Try to test the /molecules endpoint with different query parameters
@pytest.mark.parametrize(
    "page,pageSize,name,minMass,maxMass,orderBy,order",
    [
        (None, 10, None, None, None, None, None),
        (2, 21, None, None, None, None, None),
        (1, 5, "wate", None, None, None, None),
        (1, 10, None, 10, 20, None, None),
        (1, 11, None, None, None, "mass", "asc"),
        (1, 12, None, None, None, "mass", "desc")
    ],
)
def test_find_all_mock(page, pageSize, name, minMass, maxMass, orderBy, order, init_db):
    """
    Test the GET /molecules endpoint.
    """
    query_dict = {
        "page": page,
        "pageSize": pageSize,
        "name": name,
        "minMass": minMass,
        "maxMass": maxMass,
        "orderBy": orderBy,
        "order": order,
    }

    # key matches url
    key = get_key_from_url_queries("/molecules/", query_dict)

    # Initially the cache should not have the key
    # assert_key_exists_in_cache(redis, key, should_exist=False)
    response = client.get(key)

    assert response.status_code == 200

    # This should have triggered the set_json method and the cache should be set
    assert_key_exists_in_cache(redis, key, should_exist=True)
    #
    response2 = client.get(key)
    assert response2.status_code == 200

    assert response.json() == response2.json()


@pytest.mark.parametrize(
    "smiles,limit", [("CCCC", None), ("CC", 2), ("CCC", 3), ("CCCC", 3)]
)
def test_substructure_search_mock(smiles, limit, init_db):
    """
    Test the GET /molecules/search/substructures/ endpoint.
    """
    query_dict = {"smiles": smiles, "limit": limit}

    # key matches url
    key = get_key_from_url_queries("/molecules/search/substructures/", query_dict)

    # Initially the cache should not have the key
    assert_key_exists_in_cache(redis, key, should_exist=False)

    response = client.get(key)
    assert response.status_code == 200

    # This should have triggered the set_json method and the cache should be set
    assert_key_exists_in_cache(redis, key, should_exist=True)

    response2 = client.get(key)
    assert response2.status_code == 200

    assert response.json() == response2.json()


@pytest.mark.parametrize(
    "smiles,limit", [("CCCC", 10), ("CC", 2), ("CCC", 3), ("CCCC", 3)]
)
def test_superstructure_search_mock(smiles, limit, init_db):
    """
    Test the GET /molecules/search/superstructures/ endpoint.
    """
    query_dict = {"smiles": smiles, "limit": limit}

    # key matches url
    key = get_key_from_url_queries("/molecules/search/superstructures/", query_dict)

    # Initially the cache should not have the key
    assert_key_exists_in_cache(redis, key, should_exist=False)

    response = client.get(key)
    assert response.status_code == 200

    # This should have triggered the set_json method and the cache should be set
    assert_key_exists_in_cache(redis, key, should_exist=True)

    response2 = client.get(key)
    assert response2.status_code == 200

    assert response.json() == response2.json()
