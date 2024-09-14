from functools import lru_cache
from typing import Annotated

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
