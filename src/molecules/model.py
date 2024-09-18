from typing import Annotated
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base
from src.molecules.schema import MoleculeResponse


class Molecule(Base):
    """
    Molecule model class.

    Name attribute should have trigram index for fast search, I could not find a good way to do this
    declaratively in SQLModel, so did this in the migration script. I used the pg_trgm extension and gist index.

    There will be a lot of filtering and ordering on mass, so it should have an index. I also could
    not find an orm-ic way to do this(Creating Indexes and Constraints with Naming Conventions on Mixins section in
    ORM documentation looks suspicious), so I did this in the migration script as well.
    """

    molecule_id: Mapped[
        Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
    ]
    smiles: Mapped[Annotated[str, mapped_column(unique=True)]]
    name: Mapped[Annotated[str, mapped_column()]]
    # could not find a documentation for the float and numeric types in sqlalchemy yet
    # I think this will work just fine for now
    mass: Mapped[Annotated[float, mapped_column()]]

    def __repr__(self):
        return f"Molecule(molecule_id={self.molecule_id}, smiles={self.smiles}, name={self.name})"

    def to_response(self) -> MoleculeResponse:
        links = {
            "self": {
                "href": f"/molecules/{self.molecule_id}",
                "rel": "self",
                "type": "GET",
            },
            "substructures": {
                "href": f"/substructure_search?smiles={self.smiles}",
                "rel": "substructures",
                "type": "GET",
            },
        }

        return MoleculeResponse(links=links, **self.__dict__)
