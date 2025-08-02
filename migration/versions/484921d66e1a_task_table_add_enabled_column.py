"""task table add enabled column

Revision ID: 484921d66e1a
Revises: 8e2c5854dee8
Create Date: 2025-07-27 14:24:40.694258

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "484921d66e1a"
down_revision: Union[str, Sequence[str], None] = "8e2c5854dee8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "task",
        sa.Column(
            "enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("1"),
            comment="是否啟用",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("task", "enabled")