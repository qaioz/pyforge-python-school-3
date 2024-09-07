import datetime
from enum import Enum

from pydantic import BaseModel

from src.molecules.service import MoleculeService


class E(Enum):
    e1 = 1
    e2 = 2


class A(BaseModel):
    a: int


class B(A):
    b: int
    a: A
    d: datetime.datetime
    e: E


ms = MoleculeService(None, None, None)


def test_redis_key():
    b = B(a=A(a=1), b=2, d=datetime.datetime(2021, 1, 1), e=E.e1)
    print(ms._redis_key("find_all", **b.model_dump()))
    assert (
        ms._redis_key("find_all", **b.model_dump())
        == "molecules:find_all:{'a': 1}:2:2021-01-01 00:00:00:E.e1"
    )
