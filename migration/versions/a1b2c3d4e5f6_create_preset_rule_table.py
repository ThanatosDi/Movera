"""create preset_rule table

Revision ID: a1b2c3d4e5f6
Revises: f1a2b3c4d5e6
Create Date: 2026-04-12 03:00:00.000000

"""

import uuid
from datetime import UTC, datetime
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "preset_rule",
        sa.Column(
            "id",
            sa.String(),
            primary_key=True,
            default=lambda: str(uuid.uuid4()),
            unique=True,
            index=True,
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(),
            nullable=False,
            unique=True,
            index=True,
            comment="常用規則名稱",
        ),
        sa.Column(
            "rule_type",
            sa.String(),
            nullable=False,
            comment="規則引擎類型：parse 或 regex",
        ),
        sa.Column(
            "field_type",
            sa.String(),
            nullable=False,
            comment="對應欄位類型：src 或 dst",
        ),
        sa.Column(
            "pattern",
            sa.String(),
            nullable=False,
            comment="規則內容",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            default=datetime.now(UTC),
            comment="建立時間",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("preset_rule")
