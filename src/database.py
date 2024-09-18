from datetime import datetime
from functools import lru_cache
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy import func, create_engine, Engine
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


def get_database_url():
    return get_settings().database_url


@lru_cache
def get_database_engine(database_url: Annotated[str, Depends(get_database_url)]):
    return create_engine(database_url)


@lru_cache
def get_session_factory(
    database_engine: Annotated[Engine, Depends(get_database_engine)]
):
    return sessionmaker(bind=database_engine, autoflush=False, autocommit=False)
