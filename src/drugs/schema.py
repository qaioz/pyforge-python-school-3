import datetime
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from src.schema import BaseResponse
from src.drugs.model import QuantityUnit


class DrugMoleculeRequest(BaseModel):
    """
    Single molecule in the drug.

    Molecule can be referenced by molecule_id

    """

    molecule_id: Annotated[
        Optional[int],
        Field(description="Reference to the molecule, should exist in the database"),
    ]
    quantity: Annotated[
        float, Field(..., description="Quantity of the molecule in the single dose")
    ]
    quantity_unit: Annotated[
        QuantityUnit,
        Field(
            ..., description="Unit of the quantity of the molecule in the single dose"
        ),
    ]


class DrugRequest(BaseModel):
    name: Annotated[str, Field(..., min_length=1)]
    description: Annotated[Optional[str], Field()]
    molecules: Annotated[list[DrugMoleculeRequest], Field(..., min_length=1)]

    model_config = {
        # "json_encoders": {
        #     QuantityUnit: lambda v: v.value
        # },
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Coffe",
                    "description": "Best drug ever",
                    "molecules": [
                        {
                            "molecule_id": 1,
                            "quantity": 0.2,
                            "quantity_unit": "GRAM",
                        },
                        {
                            "molecule_id": 2,
                            "quantity": 5,
                            "quantity_unit": "GRAM",
                        },
                        {"molecule_id": 3, "quantity": 150, "quantity_unit": "ML"},
                    ],
                }
            ]
        }
    }


class DrugMoleculeResponse(BaseResponse):
    molecule_id: Annotated[int, Field()]
    quantity: Annotated[float, Field()]
    quantity_unit: Annotated[QuantityUnit, Field()]

    created_at: Annotated[
        datetime.datetime, Field(description="Timestamp when the entity was created")
    ] = None
    updated_at: Annotated[
        datetime.datetime, Field(description="Timestamp when the entity was updated")
    ] = None

    model_config = {
        # "json_encoders": {
        #     QuantityUnit: lambda v: v.value
        # }
    }


class DrugResponse(BaseResponse):

    drug_id: Annotated[
        int,
        Field(
            ...,
        ),
    ]
    name: Annotated[str, Field()]
    description: Annotated[Optional[str], Field()]
    molecules: Annotated[list[DrugMoleculeResponse], Field()]
