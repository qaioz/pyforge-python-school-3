"""empty message

Revision ID: e2a0ca7d84ac
Revises: 
Create Date: 2024-09-05 16:50:32.773856

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e2a0ca7d84ac"
down_revision: Union[str, None] = None
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
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("mass", sa.Float(), nullable=False),
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
        sa.ForeignKeyConstraint(["drug_id"], ["drugs.drug_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["molecule_id"], ["molecules.molecule_id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("drug_id", "molecule_id"),
    )
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("drug_molecule")
    op.drop_table("molecules")
    op.drop_table("drugs")
    # ### end Alembic commands ###