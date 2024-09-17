import enum
from os import getenv
from pydantic_settings import BaseSettings
import logging


def setup_logging():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logging.basicConfig(
        handlers=[handler],
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


class Environment(enum.Enum):
    PROD = "PROD"
    DEV = "DEV"
    TEST = "TEST"


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int

    BROKER_HOST: str
    BROKER_PORT: int
    BROKER_DB: int

    BACKEND_HOST: str
    BACKEND_PORT: int
    BACKEND_DB: int

    model_config = {
        "env_file": ".env_prod",
    }

    @property
    def database_url(self):
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class DevSettings(Settings):
    model_config = {
        "env_file": ".env_dev",
    }


class TestSettings(Settings):
    model_config = {
        "env_file": ".env_test",
    }


def get_prod_settings() -> Settings:
    return Settings()


def get_dev_settings() -> DevSettings:
    return DevSettings()


def get_test_settings() -> TestSettings:
    return TestSettings()


def get_settings() -> Settings:
    environment = getenv("ENVIRONMENT")

    if environment is None:
        raise ValueError(
            "ENVIRONMENT environment variable is not set, it should be one of PROD, DEV, TEST"
        )

    if environment == Environment.PROD.value:
        return get_prod_settings()
    elif environment == Environment.DEV.value:
        return get_dev_settings()
    elif environment == Environment.TEST.value:
        return get_test_settings()
    else:
        raise ValueError(
            "ENVIRONMENT environment variable should be one of PROD, DEV, TEST"
        )
