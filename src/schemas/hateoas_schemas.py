from pydantic import BaseModel


class Link(BaseModel):
    href: str
    rel: str
    type: str


class HATEOASResponse(BaseModel):
    links: dict[str, Link] = {}
