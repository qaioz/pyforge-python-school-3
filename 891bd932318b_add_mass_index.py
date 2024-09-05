"""add mass index

Revision ID: 891bd932318b
Revises: f57e34879583
Create Date: 2024-09-04 18:37:37.208403

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "891bd932318b"
down_revision: Union[str, None] = "f57e34879583"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE INDEX molecules_mass_idx ON molecules (mass);")


def downgrade() -> None:
    op.execute("DROP INDEX molecules_mass_idx;")
