"""add trgrm index

Revision ID: f57e34879583
Revises: 18733e4b9695
Create Date: 2024-09-03 07:19:33.496873

"""

from typing import Sequence, Union
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "f57e34879583"
down_revision: Union[str, None] = "18733e4b9695"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
    op.execute(
        "CREATE INDEX pg_trgm_on_name_idx ON molecules USING gist (name gist_trgm_ops);"
    )


def downgrade() -> None:
    op.execute("DROP INDEX pg_trgm_on_name_idx;")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm;")
