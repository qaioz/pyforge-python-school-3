"""drop molecule unique smiles for testing

Revision ID: a7f5f6d8308a
Revises: 8e97157fd633
Create Date: 2024-09-06 14:29:42.869298

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a7f5f6d8308a"
down_revision: Union[str, None] = "8e97157fd633"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    #     drop unique constraint on molecule smiles

    op.drop_constraint("molecules_smiles_key", "molecules", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint("molecules_smiles_key", "molecules", ["smiles"])
