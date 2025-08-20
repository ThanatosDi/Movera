"""create task table

Revision ID: 28d5ebf0011f
Revises:
Create Date: 2025-07-18 16:02:40.330933

"""

import uuid
from typing import Sequence, Union

import arrow
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "28d5ebf0011f"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "task",
        sa.Column(
            "id",
            sa.String(),
            primary_key=True,
            default=lambda: str(uuid.uuid4()),
            comment="UUID",
            unique=True,
            index=True,
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(),
            nullable=False,
            unique=True,
            comment="任務名稱",
            index=True,
        ),
        sa.Column(
            "include",
            sa.String(),
            nullable=False,
            comment="檔案名稱包含此字串",
            index=True,
        ),
        sa.Column("move_to", sa.String(), nullable=False, comment="移動檔案至此路徑"),
        sa.Column(
            "src_filename",
            sa.String(),
            nullable=True,
            default=None,
            comment="重新命名的來源檔案名稱",
        ),
        sa.Column(
            "dst_filename",
            sa.String(),
            nullable=True,
            default=None,
            comment="重新命名的目標檔案名稱",
        ),
        sa.Column(
            "rename_rule",
            sa.String(),
            nullable=True,
            default=None,
            comment="重新命名規則",
        ),
        sa.Column(
            "enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("1"),
            comment="是否啟用",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            default=arrow.utcnow().datetime,
            comment="建立時間",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("task")
