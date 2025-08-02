"""create tag table

Revision ID: 49aaba7db4d5
Revises: 28d5ebf0011f
Create Date: 2025-07-18 16:12:26.136314

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "49aaba7db4d5"
down_revision: Union[str, Sequence[str], None] = "28d5ebf0011f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "tag",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
            comment="自動增加 ID",
        ),
        sa.Column("name", sa.String(), nullable=False, unique=True, comment="標籤名稱"),
        sa.Column(
            "color",
            sa.String(),
            nullable=False,
            comment="Hex 標籤顏色",
        ),
        sqlite_autoincrement=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("tag")
