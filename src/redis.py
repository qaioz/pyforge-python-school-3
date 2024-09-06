from functools import lru_cache

import redis

from config import get_settings


@lru_cache
def get_redis_client():
    return redis.Redis(
        host=get_settings().REDIS_HOST, port=get_settings().REDIS_PORT, db=0
    )
