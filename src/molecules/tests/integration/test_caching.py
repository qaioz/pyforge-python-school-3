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


@pytest.mark.parametrize("idx", [random.randint(1, 10) for _ in range(5)])
def test_get_molecule_by_id(idx, init_db):
    """
    Test the GET /molecules/{molecule_id} endpoint.
    """

    # make the patched request and make sure caching is set
    with mock.patch.object(redis, "set_json") as mock_set:
        response = client.get(f"/molecules/{idx}")
        assert response.status_code == 200
        molecule_data = response.json()
        validate_response_dict_for_ith_alkane(molecule_data, idx)
        mock_set.assert_called_once()

    # Now without mocking
    response = client.get(f"/molecules/{idx}")
    assert response.status_code == 200
    molecule_data = response.json()
    validate_response_dict_for_ith_alkane(molecule_data, idx)

    # Check if the cache was set after the first request
    cache_key = f"/molecules/{idx}"

    cached_data = redis.get_json(cache_key)
    assert cached_data is not None

    # Test with cache (cache hit)
    response = client.get(f"/molecules/{idx}")
    assert response.status_code == 200
    molecule_data = response.json()
    validate_response_dict_for_ith_alkane(molecule_data, idx)

    # Now mock to see that the cache is really being used
    with mock.patch.object(redis, "get_json", return_value=cached_data) as mock_get:
        response = client.get(f"/molecules/{idx}")
        assert response.status_code == 200
        mock_get.assert_called_once_with(cache_key)

    # Now test with a header no-cache
