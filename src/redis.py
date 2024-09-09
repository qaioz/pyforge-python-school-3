from functools import lru_cache
import redis
import logging

from src.config import get_settings

logger = logging.getLogger(__name__)


class RedisCacheService:
    CACHE_EXPIRATION = 60 * 60 * 24 * 7  # 1 week

    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    def set_json(self, key, value: dict):
        self.redis_client.json().set(key, ".", value)

    def get_json(self, key) -> dict:
        return self.redis_client.json().get(key, ".")


@lru_cache
def get_redis_client():
    settings = get_settings()
    if settings.DEV_MODE:
        return redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

    if settings.TEST_MODE:
        return redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_TEST_PORT, db=0
        )

    return redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


@lru_cache
def get_redis_cache_service() -> RedisCacheService:
    return RedisCacheService(get_redis_client())
