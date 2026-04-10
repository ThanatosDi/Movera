
import uuid

from sqlalchemy import Column, ForeignKey, String, Table

from backend.database import Base

task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", String, ForeignKey("task.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String, ForeignKey("tag.id", ondelete="CASCADE"), primary_key=True),
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

    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name}, color={self.color})>"
