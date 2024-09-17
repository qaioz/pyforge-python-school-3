import redis
from src.config import get_settings

redis_client = redis.Redis(
    host=get_settings().REDIS_HOST,
    port=get_settings().REDIS_PORT,
    db=0
)

redis_celery_client = redis.Redis(
    host=get_settings().REDIS_HOST,
    port=get_settings().REDIS_PORT,
    db=1
)


def get_redis_client_celery():
    return redis_celery_client


def get_redis_client():
    return redis_client
