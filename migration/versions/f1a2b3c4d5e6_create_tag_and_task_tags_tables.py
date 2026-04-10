"""create tag and task_tags tables

Revision ID: f1a2b3c4d5e6
Revises: ac2a1cd5139c
Create Date: 2026-04-10 20:00:00.000000

"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "ac2a1cd5139c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tag",
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
            comment="標籤名稱",
        ),
        sa.Column(
            "color",
            sa.String(),
            nullable=False,
            comment="標籤顏色（預定義色票名稱）",
        ),
    )

    op.create_table(
        "task_tags",
        sa.Column(
            "task_id",
            sa.String(),
            sa.ForeignKey("task.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "tag_id",
            sa.String(),
            sa.ForeignKey("tag.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("task_tags")
    op.drop_table("tag")
