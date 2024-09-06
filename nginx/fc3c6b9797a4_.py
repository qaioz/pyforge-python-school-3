"""empty message

Revision ID: fc3c6b9797a4
Revises: 08ed502653c0
Create Date: 2024-09-06 14:15:29.278587

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "fc3c6b9797a4"
down_revision: Union[str, None] = "e2a0ca7d84ac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    #     drop unique constraint on molecule smiles

    op.drop_constraint("molecules_smiles_key", "molecules", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint("molecules_smiles_key", "molecules", ["smiles"])
