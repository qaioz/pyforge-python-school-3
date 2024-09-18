import logging

import redis

from src.redis_client import get_redis_client

logger = logging.getLogger(__name__)


class RedisCacheServiceSingleton:
    CACHE_EXPIRATION = 60 * 60 * 24 * 7  # 1 week

    __INSTANCE = None

    def __init__(self, redis_client: redis.Redis):
        """
        Be careful when using this class, it is a singleton, so it is shared between all the instances of the app

        :param redis_client:  a redis client instance
        :raises ValueError: if the instance already exists
        """
        if self.__INSTANCE is not None:
            raise ValueError(
                "Singleton instance already exists, use get_instance() to get the current instance, "
                "or create to override it."
            )
        self.redis_client = redis_client

    @classmethod
    def create(cls, redis_client: redis.Redis) -> "RedisCacheServiceSingleton":
        """
        Overwrites the current instance
        """
        cls.__INSTANCE = cls(redis_client)
        return cls.__INSTANCE

    @classmethod
    def get_instance(cls) -> "RedisCacheServiceSingleton":
        """
        Get the current instance, if it does not exist, it creates one with the default redis client

        Make sure you use create method before calling this method, if you want to use a custom redis client
        :return:
        """
        if cls.__INSTANCE is None:
            cls.create(get_redis_client())
        return cls.__INSTANCE

    def set_json(
        self, key, value: dict, expiration_seconds: int = CACHE_EXPIRATION
    ) -> None:
        """
        :param key:  the key to be used in the cache
        :param value:  the value to be cached
        :param expiration_seconds:  after this, cache will be expired, defaults to CachingService.CACHE_EXPIRATION
        """
        self.redis_client.json().set(key, ".", value)
        self.redis_client.expire(key, expiration_seconds)

    def get_json(self, key) -> dict:
        """
        :param key:  the key to be used in the cache
        :return:  the value from the cache, if it exists, otherwise None
        """
        return self.redis_client.json().get(key, ".")
