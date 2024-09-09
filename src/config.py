from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
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


class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    DEV_MODE: bool
    TEST_MODE: bool
    TEST_DB_URL: str
    DEV_DB_URL: str
    CONTEXT_PATH: str

    REDIS_HOST: str
    REDIS_PORT: int

    REDIS_TEST_PORT: int

    model_config = SettingsConfigDict(
        env_file=".env",
        # env_file="/home/gaioz/quantori/pyforge-python-school-3/.env",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        if self.DEV_MODE and self.TEST_MODE:
            raise ValueError("Cannot run in DEV and TEST mode at the same time")

        if self.DEV_MODE:
            return self.DEV_DB_URL

        if self.TEST_MODE:
            return self.TEST_DB_URL

        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
