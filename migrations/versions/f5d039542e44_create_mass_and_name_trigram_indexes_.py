"""create mass and name trigram indexes and unique key on smiles

Revision ID: f5d039542e44
Revises: a7f5f6d8308a
Create Date: 2024-09-06 14:32:35.545662

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f5d039542e44"
down_revision: Union[str, None] = "a7f5f6d8308a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX molecules_name_pg_trgm_idx ON molecules USING gist (name gist_trgm_ops);"
    )
    op.execute("CREATE INDEX molecules_mass_idx ON molecules (mass);")


def downgrade() -> None:
    op.execute("DROP INDEX molecules_name_pg_trgm_idx;")
    op.execute("DROP INDEX molecules_mass_idx;")
