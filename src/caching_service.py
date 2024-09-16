import functools
import inspect
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
    def create(cls, redis_client: redis.Redis):
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

    def set_json(self, key, value: dict, expiration_seconds: int = None):
        self.redis_client.json().set(key, ".", value)
        self.redis_client.expire(key, expiration_seconds or self.CACHE_EXPIRATION)

    def get_json(self, key) -> dict:
        return self.redis_client.json().get(key, ".")

    @staticmethod
    def generate_caching_key(key_prefix: str, key_args: list[str], **kwargs) -> str:
        # filter out None values and those that are not in key_args also, it is important to sort the kwargs
        # according to argument name to make sure that the key is always the same, regardless of the order
        filtered_sorted_kwargs_tuples = sorted(
            [
                (k, v)
                for k, v in kwargs.items()
                if v is not None and (not key_args or k in key_args)
            ]
        )

        key_builder = [key_prefix]

        for k, v in filtered_sorted_kwargs_tuples:
            key_builder.append(f"{k}={v}")

        return ":".join(key_builder)


def cached(
    key_prefix: str = None,
    key_args: list[str] = None,
    expiration_seconds: int = None,
    ignore_self: bool = True,
    map_return: callable = None,
):
    """
    :param key_prefix: how the key should be prefixed, if None, function name is used
    :param key_args:  which arguments should be used in the key, if None, all arguments are used
    :param expiration_seconds:  how long the cache should be valid, defaults to CachingService.CACHE_EXPIRATION
    :param ignore_self: Useful for instance methods, if True, self is ignored in the caching key, even if it is included
    in the key_args
    :param map_return: a function that maps the return value before caching, useful for model serialization, if
    the return type is not json_serializable for redis client
    """
    def wrapper(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            # we need every argument to be in keyword, so we need to get the function signature and bind the arguments
            bound_args = inspect.signature(func).bind(*args, **kwargs)
            bound_args.apply_defaults()
            keyword_arguments = dict(bound_args.arguments)
            if ignore_self and "self" in keyword_arguments:
                keyword_arguments.pop("self", None)

            if expiration_seconds is None:
                expiration_seconds_ = RedisCacheServiceSingleton.CACHE_EXPIRATION
            else:
                expiration_seconds_ = expiration_seconds

            if key_prefix is None:
                prefix = func.__name__
            else:
                prefix = key_prefix

            if key_args is None:
                key_args_ = []
            else:
                key_args_ = key_args

            key = RedisCacheServiceSingleton.generate_caching_key(
                prefix, key_args_, **keyword_arguments
            )
            RedisCacheServiceSingleton.get_instance()
            cache = RedisCacheServiceSingleton.get_instance().get_json(key)

            if cache:
                logger.info("Cache hit for key: " + key)
                if not (
                    "cache_control" in keyword_arguments
                    and keyword_arguments["cache_control"] is not None
                    and "no-cache" in keyword_arguments["cache_control"]
                ):
                    return cache
                logger.info("Cache is ignored due to cache-control header, revalidating cache.")
            else:
                logger.info("Cache miss for key: " + key)

            result = func(*args, **kwargs)
            if map_return:
                result = map_return(result)
            RedisCacheServiceSingleton.get_instance().set_json(
                key, result, expiration_seconds=expiration_seconds_
            )
            return result

        return wrapped

    return wrapper
