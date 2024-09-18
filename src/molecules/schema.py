from typing import Annotated, Literal
from black.linegen import Optional
from pydantic import BaseModel, Field, field_validator
from src.molecules.exception import InvalidSmilesException
from src.molecules.utils import is_valid_smiles
from src.schema import Link


class MoleculeRequest(BaseModel):
    smiles: Annotated[
        str,
        Field(
            min_length=1,
            description="SMILES string of the molecule, should be unique",
        ),
    ]
    name: Annotated[Optional[str], Field(description="Name of the molecule")]

    @field_validator("smiles")
    @classmethod
    def validate_smiles(cls, smiles: str):
        if not is_valid_smiles(smiles):
            raise InvalidSmilesException(smiles)
        return smiles

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "smiles": "C",
                    "name": "Methane",
                }
            ]
        }
    }


class MoleculeResponse(BaseModel):
    molecule_id: Annotated[int, Field(description="Unique identifier for the molecule")]
    smiles: Annotated[str, Field(description="SMILES string of the molecule")]
    name: Annotated[Optional[str], Field(description="Name of the molecule")]
    mass: Annotated[float, Field(description="Molecular mass of the molecule")]
    created_at: Annotated[
        str, Field(description="Timestamp when the molecule was created")
    ] = None
    updated_at: Annotated[
        str, Field(description="Timestamp when the molecule was updated")
    ] = None
    links: Annotated[
        dict[str, Link],
        Field(description="Links to self and substructures and superstructures"),
    ]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "molecule_id": 1,
                    "smiles": "C",
                    "name": "Methane",
                    "mass": 16.04,
                    "created_at": "2021-06-01T12:00:00",
                    "updated_at": "2021-06-01T12:00:00",
                    "links": {
                        "self": {
                            "href": "/molecules/1",
                            "rel": "self",
                            "type": "GET",
                        },
                        "substructures": {
                            "href": "/molecules/search/substructures?smiles={C}",
                            "rel": "substructures",
                            "type": "GET",
                        },
                        "superstructures": {
                            "href": "/molecules/search/superstructures?smiles={C}",
                            "rel": "superstructures",
                            "type": "GET",
                        },
                    },
                }
            ]
        }
    }


class MoleculeCollectionResponse(BaseModel):
    """
    Response schema for the collection of molecules

    If this is a response from substances search, you will not see pagination attributes
    page, pageSize, and links will be empty.


    """

    total: Annotated[int, Field(..., description="Total number of molecules")]
    page: Annotated[Optional[int], Field(description="Current page number")]
    page_size: Annotated[Optional[int], Field(description="Number of items per page")]
    data: Annotated[list[MoleculeResponse], Field(description="List of molecules")]
    links: Annotated[
        dict[str, Link],
        Field(
            description="nextPage and previousPage links. If current page is 0, "
            "previousPage will be empty"
        ),
    ]


# list for order_by possible values are "mass" for now, but can be extended in the future
order_by_values = Literal["mass"]
order_values = Literal["asc", "desc"]


class SearchParams(BaseModel):
    name: Annotated[Optional[str], Field(description="Name of the molecule")]
    min_mass: Annotated[
        Optional[float], Field(description="Minimum mass of the molecule", ge=0)
    ]
    max_mass: Annotated[
        Optional[float], Field(description="Maximum mass of the molecule", ge=0)
    ]
    order_by: Annotated[Optional[order_by_values], Field(description="Order by mass")]
    order: Annotated[
        Optional[order_values], Field(description="Order ascending or descending")
    ]


def get_search_params(
    name: Optional[str] = None,
    minMass: Optional[float] = None,
    maxMass: Optional[float] = None,
    orderBy: Optional[order_by_values] = None,
    order: Optional[order_values] = None,
):
    return SearchParams(
        name=name,
        min_mass=minMass,
        max_mass=maxMass,
        order_by=orderBy,
        order=order,
    )
