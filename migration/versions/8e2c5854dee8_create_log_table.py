"""create log table

Revision ID: 8e2c5854dee8
Revises: 28d5ebf0011f
Create Date: 2025-07-20 03:11:54.462949

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8e2c5854dee8"
down_revision: Union[str, Sequence[str], None] = "28d5ebf0011f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "log",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
            comment="自動增加 ID",
        ),
        sa.Column(
            "task_id",
            sa.String(),
            sa.ForeignKey("task.id"),
            nullable=False,
            comment="任務 ID",
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
    op.drop_table("log")
