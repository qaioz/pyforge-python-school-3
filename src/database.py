from datetime import datetime
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy import func, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
    mapped_column,
    Mapped,
    sessionmaker,
)

from src.config import get_settings

created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[
    datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)
]


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]


@lru_cache
def get_database_url():
    if get_settings().DEV_MODE and get_settings().TEST_MODE:
        raise ValueError("Cannot run in DEV and TEST mode at the same time")

    if get_settings().DEV_MODE:
        return get_settings().DEV_DB_URL

    if get_settings().TEST_MODE:
        return get_settings().TEST_DB_URL


@lru_cache
def get_session_factory(database_url: Annotated[str, Depends(get_database_url)]):
    return sessionmaker(
        bind=create_engine(database_url), autoflush=False, autocommit=False
    )
