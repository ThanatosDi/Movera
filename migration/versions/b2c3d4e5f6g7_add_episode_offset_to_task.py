"""add episode offset fields to task table

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-04-14 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c3d4e5f6g7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """新增 episode 偏移相關欄位至 task 表。"""
    op.add_column(
        "task",
        sa.Column(
            "episode_offset_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
            comment="是否啟用 episode 偏移",
        ),
    )
    op.add_column(
        "task",
        sa.Column(
            "episode_offset_group",
            sa.String(),
            nullable=True,
            comment="偏移目標的 group 名稱",
        ),
    )
    op.add_column(
        "task",
        sa.Column(
            "episode_offset_value",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
            comment="episode 偏移量",
        ),
    )


def downgrade() -> None:
    """移除 episode 偏移相關欄位。"""
    with op.batch_alter_table("task") as batch_op:
        batch_op.drop_column("episode_offset_value")
        batch_op.drop_column("episode_offset_group")
        batch_op.drop_column("episode_offset_enabled")
