"""create_setting_table

Revision ID: d6630c6f431c
Revises: 8e2c5854dee8
Create Date: 2025-09-06 17:49:29.813436

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import table as sql_table, column as sql_column

# revision identifiers, used by Alembic.
revision: str = "d6630c6f431c"
down_revision: Union[str, Sequence[str], None] = "8e2c5854dee8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

table = "setting"


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        table,
        sa.Column(
            "key",
            sa.String(),
            primary_key=True,
            nullable=False,
            comment="設定名稱",
            index=True,
        ),
        sa.Column(
            "value",
            sa.String(),
            nullable=False,
            comment="設定值",
        ),
        sa.Column(
            "description",
            sa.String(),
            nullable=False,
            comment="設定說明",
        ),
    )

    default_setting = [
        {"key": "timezone", "value": "UTC", "description": "時區"},
        {"key": "log_level", "value": "INFO", "description": "日誌等級"},
        {"key": "locale", "value": "zh_TW", "description": "語言"},
    ]
    # Insert default settings after table creation
    setting_table = sql_table(
        table,
        sql_column("key", sa.String()),
        sql_column("value", sa.String()),
        sql_column("description", sa.String()),
    )
    op.bulk_insert(setting_table, default_setting)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table(table)
