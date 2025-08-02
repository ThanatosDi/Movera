import os
import uuid

import arrow
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
    event,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

# 從環境變數取得 SQLITE 路徑，預設 ./database/database.db
sqlite_path = os.getenv("SQLITE_PATH", "./database/database.db")
engine = create_engine(f"sqlite:///{sqlite_path}", echo=True)


# 監聽資料庫連線事件，並啟用外鍵約束
@event.listens_for(Engine, "connect")
def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute("PRAGMA foreign_keys=ON")


session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    db = session()
    try:
        yield db
    finally:
        db.close()


class Base(DeclarativeBase): ...


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
        index=True,
        nullable=False,
    )
    include = Column(
        String,
        nullable=False,
        index=True,
    )
    move_to = Column(
        String,
        nullable=False,
    )
    src_filename_regex = Column(
        String,
        nullable=True,
        default=None,
        comment="來源檔案名稱正規表達式",
    )
    dst_filename_regex = Column(
        String,
        nullable=True,
        default=None,
        comment="重新命名檔案名稱正規表達式",
    )
    enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="是否啟用",
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=arrow.utcnow().datetime,
        comment="建立時間",
    )

    logs = relationship("Log", back_populates="task", order_by="Log.timestamp.desc()")
    tags = relationship("Tag", secondary="task_tag_mapping", back_populates="tasks")


class Tag(Base):
    __tablename__ = "tag"
    sqlite_autoincrement = True

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="自動增加 ID",
    )

    name = Column(
        String,
        nullable=False,
        unique=True,
        comment="標籤名稱",
    )

    color = Column(
        String,
        nullable=False,
        comment="Hex 標籤顏色",
    )

    tasks = relationship("Task", secondary="task_tag_mapping", back_populates="tags")


class TaskTagMapping(Base):
    __tablename__ = "task_tag_mapping"
    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        index=True,
        nullable=False,
    )
    task_id = Column(String, ForeignKey("task.id"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tag.id"), primary_key=True)


class Log(Base):
    __tablename__ = "log"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, ForeignKey("task.id"))
    level = Column(String)
    message = Column(String)
    timestamp = Column(
        DateTime,
        default=lambda: arrow.utcnow().datetime,
        nullable=False,
        comment="日誌時間戳",
    )

    task = relationship("Task", back_populates="logs")
