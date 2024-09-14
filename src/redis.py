from functools import lru_cache
from typing import Annotated, Type

import redis
import logging

from fastapi import Depends

from src.config import get_settings, Settings

logger = logging.getLogger(__name__)


class RedisCacheService:
    CACHE_EXPIRATION = 60 * 60 * 24 * 7  # 1 week

    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    def set_json(self, key, value: dict):
        self.redis_client.json().set(key, ".", value)

    def get_json(self, key) -> dict:
        return self.redis_client.json().get(key, ".")

    def cached(self, key_prefix: str = None, key_args: list[str] = None):
        def wrapper(func):
            def wrapped(*args, **kwargs):
                if args:
                    raise ValueError("Cached function must not have positional arguments")

                key = self.generate_caching_key(key_prefix, key_args, **kwargs)
                cached = self.get_json(key)
                if cached:
                    return cached
                result = func(*args, **kwargs)
                self.set_json(key, result)
                return result

            return wrapped

        return wrapper

    @staticmethod
    def generate_caching_key(key_prefix: str, key_args: list[str], **kwargs) -> str:
        # filter out None values and those that are not in key_args also, it is important to sort the kwargs
        # according to argument name to make sure that the key is always the same, regardless of the order
        filtered_sorted_kwargs_tuples = sorted([
            (k, v) for k, v in kwargs.items() if v is not None and (not key_args or k in key_args)
        ])

        key_builder = [key_prefix]

        for k, v in filtered_sorted_kwargs_tuples:
            key_builder.append(f"{k}={v}")

        return ":".join(key_builder)


def get_redis_credentials(settings: Annotated[Settings, Depends(get_settings)]) -> dict:
    return dict(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,
    )


def get_redis_client(
        redis_credentials: Annotated[dict, Depends(get_redis_credentials)]
) -> redis.Redis:
    client = redis.Redis(
        host=redis_credentials["host"], port=redis_credentials["port"], db=0
    )
    if not hasattr(get_redis_client, "client"):
        get_redis_client.client = client
    return get_redis_client.client


@lru_cache
def get_redis_cache_service(
        redis_client: Annotated[redis.Redis, Depends(get_redis_client)]
) -> RedisCacheService:
    return RedisCacheService(redis_client)
