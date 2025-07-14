from datetime import datetime

from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    __tablename__ = "task"

    name: str = Field(
        max_length=255,
        primary_key=True,
        description="任務名稱",
        unique=True,
        index=True,
    )
    include: str = Field(
        max_length=255,
        description="檔案名稱包含該字串",
    )
    move_to: str = Field(
        max_length=255,
        description="移動至的目標資料夾",
    )
    src_filename_regex: str = Field(
        max_length=255,
        description="來源檔案名稱的正規表示式",
    )
    dst_filename_regex: str = Field(
        max_length=255,
        description="目標檔案名稱的正規表示式",
    )

    def __str__(self):
        return f"Task(name='{self.name}', include='{self.include}', move_to='{self.move_to}', src_filename_regex='{self.src_filename_regex}', dst_filename_regex='{self.dst_filename_regex}')"


class Tag(SQLModel, table=True):
    __tablename__ = "tag"

    name: str = Field(
        max_length=255,
        primary_key=True,
        description="標籤名稱",
        unique=True,
        index=True,
    )

    color: str = Field(
        max_length=255,
        description="標籤顏色",
    )

    def __str__(self):
        return f"Tag(name='{self.name}', color='{self.color}')"


class TaskTagMapping(SQLModel, table=True):
    __tablename__ = "task_tag_mapping"
    __table_args__ = {"sqlite_autoincrement": True}

    id: int = Field(default=None, primary_key=True, description="主鍵")
    task_name: str = Field(
        max_length=255,
        description="任務名稱",
        foreign_key="task.name",
    )
    tag_name: str = Field(
        max_length=255,
        description="標籤名稱",
        foreign_key="tag.name",
    )

    def __str__(self):
        return f"TaskTagMapping(id='{self.id}', task_name='{self.task_name}', tag_name='{self.tag_name}')"


class Log(SQLModel, table=True):
    __tablename__ = "log"
    __table_args__ = {"sqlite_autoincrement": True}

    id: int = Field(
        default=None,
        primary_key=True,
        description="主鍵",
    )

    task_name: str = Field(
        max_length=255,
        description="任務名稱",
        foreign_key="task.name",
    )

    level: str = Field(
        max_length=255,
        description="日誌等級",
    )
    message: str = Field(
        max_length=255,
        description="日誌訊息",
    )
    timestamp: datetime = Field(max_length=255, description="日誌時間")

    def __str__(self):
        return f"Log(id='{self.id}', task_name='{self.task_name}', level='{self.level}', message='{self.message}', timestamp='{self.timestamp}')"


class Setting(SQLModel, table=True):
    __tablename__ = "setting"

    name: str = Field(
        max_length=255,
        description="設定名稱",
        primary_key=True,
        unique=True,
        index=True,
    )

    value: str = Field(
        max_length=255,
        description="設定值",
    )

    def __str__(self):
        return f"Setting(name='{self.name}', value='{self.value}')"
