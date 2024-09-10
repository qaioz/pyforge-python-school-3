from unittest import mock

from src.redis import RedisCacheService


def assert_set_json_called_with_url(
    client, redis: RedisCacheService, url, should_be_called, headers=None
):
    """
    This is helpful method fot **UNIT** testing the caching mechanism.

    Checks if the set_json method of the RedisCacheService is being called after the get request.

    Does not check if the method is being called with the correct parameters, just checks if it is being called.
    that is very hard and requires a lot of mocking of implementation details. Instead, correctness will be easily
    checked in the integration tests.

    :param client: TestClient instance
    :param redis: Instance of the RedisCacheService
    :param url: URL to be tested
    :param should_be_called: is a boolean that indicates if the set_json method should be called or not.
    logic is simple, if the URL is not in the cache, it should be called, otherwise it should not be called.
    """

    with mock.patch.object(redis, "set_json") as mock_set:
        if not headers:
            response = client.get(url)
        else:
            response = client.get(url, headers=headers)
        assert response.status_code == 200
        if should_be_called:
            mock_set.assert_called_once()
        else:
            mock_set.assert_not_called()


def assert_key_exists_in_cache(
    redis_cache_service: RedisCacheService, key, should_exist
):
    """
    Check if a key exists in the cache or not.
    """

    if should_exist:
        assert redis_cache_service.get_json(key) is not None
    else:
        assert redis_cache_service.get_json(key) is None


def get_key_from_url_queries(url: str, query_params: dict):
    sorted_query_params = sorted(
        (k, v) for k, v in query_params.items() if v is not None
    )
    return (
        url + "?" + "&".join([f"{k}={v}" for k, v in sorted_query_params])
        if len(sorted_query_params) > 0
        else url
    )
