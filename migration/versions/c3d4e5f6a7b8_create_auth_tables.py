"""create user and webhook_token tables

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6g7
Create Date: 2026-06-23 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6g7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user",
        sa.Column(
            "username",
            sa.String(),
            primary_key=True,
            nullable=False,
            comment="管理員使用者名稱",
        ),
        sa.Column(
            "password_hash",
            sa.String(),
            nullable=False,
            comment="sha256(salt + 前端傳入的 sha256 值)",
        ),
        sa.Column("salt", sa.String(), nullable=False, comment="每帳號隨機 salt"),
        sa.Column("created_at", sa.DateTime(), nullable=False, comment="建立時間"),
    )

    op.create_table(
        "webhook_token",
        sa.Column(
            "id",
            sa.String(),
            primary_key=True,
            unique=True,
            index=True,
            nullable=False,
            comment="UUID",
        ),
        sa.Column("name", sa.String(), nullable=False, comment="token 名稱"),
        sa.Column(
            "token_hash",
            sa.String(),
            nullable=False,
            unique=True,
            index=True,
            comment="sha256(明文 token)",
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False, comment="建立時間"),
        sa.Column(
            "revoked_at",
            sa.DateTime(),
            nullable=True,
            comment="撤銷時間，NULL 表示有效",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("webhook_token")
    op.drop_table("user")
