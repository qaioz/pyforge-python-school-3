"""empty message

Revision ID: 4ec9189262bd
Revises: 9f3c7d8e12a9
Create Date: 2024-08-28 16:12:50.644239

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4ec9189262bd"
down_revision: Union[str, None] = "9f3c7d8e12a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "drugs",
        sa.Column("drug_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("drug_id"),
    )
    op.create_table(
        "molecules",
        sa.Column("molecule_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("smiles", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("molecule_id"),
        sa.UniqueConstraint("smiles"),
    )
    op.create_table(
        "drug_molecule",
        sa.Column("drug_id", sa.Integer(), nullable=False),
        sa.Column("molecule_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Float(), nullable=False),
        sa.Column(
            "quantity_unit",
            sa.Enum("MOLAR", "MASS", "VOLUME", name="quantityunit"),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["drug_id"],
            ["drugs.drug_id"],
        ),
        sa.ForeignKeyConstraint(
            ["molecule_id"],
            ["molecules.molecule_id"],
        ),
        sa.PrimaryKeyConstraint("drug_id", "molecule_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("drug_molecule")
    op.drop_table("molecules")
    op.drop_table("drugs")
    # ### end Alembic commands ###