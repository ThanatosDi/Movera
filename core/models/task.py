# core/models/task.py
import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, String, func
from sqlalchemy.orm import relationship

from core.database import Base


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

    def __repr__(self):
        return f"<Task(id={self.id}, name={self.name})>"
