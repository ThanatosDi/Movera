"""create system log table

Revision ID: ac2a1cd5139c
Revises: d6630c6f431c
Create Date: 2025-11-19 16:30:14.508109

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ac2a1cd5139c"
down_revision: Union[str, Sequence[str], None] = "d6630c6f431c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "system_log",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
            comment="自動增加 ID",
        ),
        sa.Column("level", sa.String(), nullable=False, comment="日誌等級"),
        sa.Column("message", sa.String(), nullable=False, comment="日誌訊息"),
        sa.Column(
            "timestamp",
            sa.DateTime(),
            nullable=False,
            comment="日誌時間",
        ),
        sqlite_autoincrement=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("system_log")
