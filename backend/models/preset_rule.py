import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, String

from backend.database import Base


class PresetRule(Base):
    __tablename__ = "preset_rule"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        index=True,
        nullable=False,
    )
    name = Column(
        String,
        unique=True,
        nullable=False,
        index=True,
        comment="常用規則名稱",
    )
    rule_type = Column(
        String,
        nullable=False,
        comment="規則引擎類型：parse 或 regex",
    )
    field_type = Column(
        String,
        nullable=False,
        comment="對應欄位類型：src 或 dst",
    )
    pattern = Column(
        String,
        nullable=False,
        comment="規則內容",
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now(UTC),
        comment="建立時間",
    )

    def __repr__(self):
        return f"<PresetRule(id={self.id}, name={self.name}, rule_type={self.rule_type}, field_type={self.field_type})>"
