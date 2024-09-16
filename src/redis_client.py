import redis
from src.config import get_settings

redis_client = redis.Redis(
    host=get_settings().REDIS_HOST,
    port=get_settings().REDIS_PORT,
    db=0,
)


def get_redis_client():
    return redis_client
