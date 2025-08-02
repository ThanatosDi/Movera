"""create task and tag mapping table

Revision ID: b19a8deb7481
Revises: 49aaba7db4d5
Create Date: 2025-07-18 18:12:05.764812

"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b19a8deb7481"
down_revision: Union[str, Sequence[str], None] = "49aaba7db4d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "task_tag_mapping",
        sa.Column(
            "id", sa.String(),
            primary_key=True,
            default=lambda: str(uuid.uuid4()),
            comment="UUID",
            unique=True,
            index=True,
            nullable=False,
        ),
        sa.Column(
            "task_id",
            sa.String(),
            sa.ForeignKey("task.id"),
            nullable=False,
            comment="任務 ID",
        ),
        sa.Column(
            "tag_id",
            sa.Integer(),
            sa.ForeignKey("tag.id"),
            nullable=False,
            comment="標籤 ID",
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("task_tag_mapping")
