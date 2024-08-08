from pydantic import BaseModel, field_validator
from .exception import ValidationException


class CreateCollection(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, name):
        if not name:
            raise ValidationException("Name cannot be empty.")
        if not name.isalnum():
            raise ValidationException("Name can only contain alphanumeric characters.")
        return name


class CreateDocument(BaseModel):
    data: dict



