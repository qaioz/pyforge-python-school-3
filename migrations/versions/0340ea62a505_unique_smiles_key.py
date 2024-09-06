"""unique smiles key

Revision ID: 0340ea62a505
Revises: f5d039542e44
Create Date: 2024-09-06 18:13:53.714809

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0340ea62a505"
down_revision: Union[str, None] = "f5d039542e44"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint("molecules_smiles_key", "molecules", ["smiles"])


def downgrade() -> None:
    op.drop_constraint("molecules_smiles_key", "molecules", type_="unique")
