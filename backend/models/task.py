import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from backend.models.tag import task_tags

from backend.database import Base


class Task(Base):
    __tablename__ = "task"

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
    )
    include = Column(
        String,
        nullable=False,
    )
    move_to = Column(
        String,
        nullable=False,
    )
    src_filename = Column(
        String,
        nullable=True,
        default=None,
        comment="來源檔案名稱規則",
    )
    dst_filename = Column(
        String,
        nullable=True,
        default=None,
        comment="重新命名規則的目標檔案名稱",
    )
    rename_rule = Column(
        String,
        nullable=True,
        default=None,
        comment="重新命名規則",
    )
    episode_offset_enabled = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否啟用 episode 偏移",
    )
    episode_offset_group = Column(
        String,
        nullable=True,
        default=None,
        comment="偏移目標的 group 名稱",
    )
    episode_offset_value = Column(
        Integer,
        default=0,
        nullable=False,
        comment="episode 偏移量",
    )
    enabled = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否啟用",
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.now(UTC),
        comment="建立時間",
    )

    logs = relationship(
        "Log",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="Log.timestamp.desc()",
    )

    tags = relationship(
        "Tag",
        secondary=task_tags,
        lazy="selectin",
        order_by=task_tags.c.created_at.asc(),
    )

    def __repr__(self):
        return f"<Task(id={self.id}, name={self.name})>"
