from __future__ import annotations
import enum
from typing import List, Optional
from sqlalchemy import ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base


class QuantityUnit(enum.Enum):
    MOLAR = "MOLAR"
    MASS = "GRAM"
    VOLUME = "ML"


class DrugMolecule(Base):
    """
    This table is used to store the relationship between drugs and molecules.

    Deleting a molecule should not be allowed if it is used in a drug, but deleting a drug should
    delete all the related drug_molecule entries.
    """

    __tablename__ = "drug_molecule"

    drug_id: Mapped[int] = mapped_column(
        ForeignKey("drugs.drug_id", ondelete="CASCADE"), primary_key=True
    )
    molecule_id: Mapped[int] = mapped_column(
        ForeignKey("molecules.molecule_id", ondelete="RESTRICT"), primary_key=True
    )
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    quantity_unit: Mapped[QuantityUnit] = mapped_column(nullable=False)


class Drug(Base):
    __tablename__ = "drugs"

    drug_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)

    # Define the relationship with DrugMolecule
    molecules: Mapped[List[DrugMolecule]] = relationship("DrugMolecule")
