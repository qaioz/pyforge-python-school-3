"""empty message

Revision ID: 08ed502653c0
Revises: e2a0ca7d84ac
Create Date: 2024-09-05 16:50:40.934947

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "08ed502653c0"
down_revision: Union[str, None] = "e2a0ca7d84ac"
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
