
import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Table, func

from backend.database import Base

task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", String, ForeignKey("task.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String, ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "created_at",
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        comment="標籤加入任務的時刻",
    ),
)


class Tag(Base):
    __tablename__ = "tag"

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
        comment="標籤名稱",
    )
    color = Column(
        String,
        nullable=False,
        comment="標籤顏色（預定義色票名稱）",
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now(UTC),
        comment="建立時間",
    )

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name}, color={self.color})>"
