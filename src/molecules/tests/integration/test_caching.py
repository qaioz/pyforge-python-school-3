# import os
# import random
# import pytest
# import unittest.mock as mock
# from fastapi.testclient import TestClient
# from sqlalchemy import create_engine, text
# from sqlalchemy.orm import sessionmaker
# from src.config import get_settings
# from src.database import Base
# from src.main import app
# from src.molecules.repository import MoleculeRepository
# from src.molecules.schema import MoleculeRequest
# from src.molecules.service import get_molecule_service, MoleculeService
# from src.molecules.tests.generate_csv_file import generate_testing_files
# from src.molecules.tests.testing_utils import (
#     alkane_request_jsons,
#     validate_response_dict_for_ith_alkane,
#     validate_response_dict_for_alkane,
#     heptane_isomer_requests,
#     get_imaginary_alkane_requests,
# )
# from src.redis import RedisCacheService, get_redis_client
# import redis
#
# engine = create_engine(
#     get_settings().TEST_DB_URL,
# )
# session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
# molecule_repository = MoleculeRepository()
#
# redis_test_client = redis.Redis("localhost", get_settings().REDIS_TEST_PORT, db=0)
# redis = RedisCacheService(redis_test_client)
# redis.CACHE_EXPIRATION = 30
# molecule_service = MoleculeService(
#     molecule_repository, session_factory, redis
# )
#
#
# client = TestClient(app)
# app.dependency_overrides[get_molecule_service] = lambda: molecule_service
#
#
# @pytest.fixture
# def init_db():
#     """
#     Create the database schema and add first 100 alkanes to the database.
#
#     Also delete all keys from the test Redis database.
#     """
#
#     # redis_test_client.flushdb()
#     Base.metadata.drop_all(engine)
#     Base.metadata.create_all(engine)
#     #
#     with engine.connect() as conn:
#         conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
#         conn.execute(
#             text(
#                 "CREATE INDEX IF NOT EXISTS pg_trgm_on_name_idx ON molecules USING gist (name gist_trgm_ops);"
#             )
#         )
#         conn.commit()
#
#     for i in range(1, 100):
#         molecule_service.save(MoleculeRequest.model_validate(alkane_request_jsons[i]))
#
#
# # @pytest.mark.parametrize("idx", [random.randint(1, 100) for _ in range(5)])
# def test_get_molecule_by_id(init_db):
#     idx = 10
#     """
#     Test the GET /molecules/{molecule_id} endpoint.
#     """
#     # Test without cache (cache miss)
#     response = client.get(f"/molecules/{idx}")
#     assert response.status_code == 200
#     molecule_data = response.json()
#     validate_response_dict_for_ith_alkane(molecule_data, idx)
#
#
#     #
#
#     # Check if the cache was set after the first request
#     cache_key = f"molecules/{idx}"
#     cached_data = redis.get_json(cache_key)
#     all_keys = redis_test_client.keys()
#     print(all_keys)
#     assert cached_data is not None
#     validate_response_dict_for_ith_alkane(cached_data, idx)
#
#     # Test with cache (cache hit)
#     # with mock.patch.object(molecule_service._redis, "get_json", return_value=cached_data) as mock_cache:
#     #     response = client.get(f"/molecules/{idx}")
#     #     assert response.status_code == 200
#     #     assert response.json() == cached_data
#     #     mock_cache.assert_called_once_with(cache_key)
#     #
