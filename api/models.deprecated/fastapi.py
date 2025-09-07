import uuid
from datetime import datetime

import arrow
from pydantic import BaseModel, ConfigDict, Field


class HTTPError(BaseModel):
    detail: str
    model_config = ConfigDict(
        json_schema_extra={"example": {"detail": "Error message"}}
    )


class UUID(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="任務 UUID，自動產生",
        json_schema_extra={"example": "03990e8d-e3e6-4040-b3f1-12840e34912f"},
    )


class Autoincrement(BaseModel):
    id: int = Field(
        default=1,
        description="自動增加 ID",
        json_schema_extra={"example": 1},
    )


class TaskFields(BaseModel):
    name: str = Field(
        ...,
        description="任務名稱",
        json_schema_extra={"example": "公爵千金的家庭教師"},
    )
    include: str = Field(
        ...,
        description="檔案名稱包含的字串",
        json_schema_extra={"example": "公爵千金的家庭教師"},
    )
    move_to: str = Field(
        ...,
        description="移動檔案至此路徑",
        json_schema_extra={"example": "/Users/username/Downloads"},
    )
    src_filename_regex: str | None = Field(
        ...,
        description="來源檔案名稱的正規表示法",
        json_schema_extra={"example": "(.+公爵千金的家庭教師 - )(\d{2})( .+)\\.mp4"},
    )
    dst_filename_regex: str | None = Field(
        ...,
        description="重新命名目標檔案名稱的正規表示法",
        json_schema_extra={"example": "\\1S01E\\2\\3.mp4"},
    )
    enabled: bool = Field(
        ...,
        description="是否啟用",
        json_schema_extra={"example": True},
    )


class CreatedAtModel(BaseModel):
    created_at: datetime = Field(
        default_factory=lambda: arrow.utcnow().datetime,
        description="任務建立時間，自動產生",
        json_schema_extra={"example": "2025-07-18 18:04:56.399250"},
    )


class TagField(BaseModel):
    name: str = Field(
        ...,
        description="標籤名稱",
        json_schema_extra={"example": "2025 07月夏番"},
    )
    color: str = Field(
        ...,
        description="標籤顏色",
        json_schema_extra={"example": "#ff0000"},
    )


class Task(CreatedAtModel, TaskFields, UUID):
    tags: list["Tag"] = []
    logs: list["Log"] = []
    model_config = ConfigDict(from_attributes=True)


class TaskCreate(TaskFields): ...


class TaskUpdate(TaskFields): ...


class TagUpdate(TagField): ...


class Tag(TagField, Autoincrement):
    model_config = ConfigDict(from_attributes=True)


class TagCreate(TagField): ...


class TaskTagMapping(UUID):
    task_id: str = Field(
        ...,
        description="任務 UUID",
        json_schema_extra={"example": "03990e8d-e3e6-4040-b3f1-12840e34912f"},
    )
    tag_id: int = Field(
        ...,
        description="標籤 ID",
        json_schema_extra={"example": 1},
    )


class LogFields(BaseModel):
    task_id: str | None = Field(None, description="關聯的任務 ID")
    level: str = Field(
        ...,
        description="日誌等級 (e.g., INFO, ERROR)",
        json_schema_extra={"example": "INFO"},
    )
    message: str = Field(
        ...,
        description="日誌訊息",
        json_schema_extra={"example": "File moved successfully."},
    )


class Log(LogFields, Autoincrement):
    timestamp: datetime = Field(
        ..., description="日誌時間戳", default_factory=lambda: arrow.utcnow().datetime
    )
    model_config = ConfigDict(from_attributes=True)


class LogCreate(LogFields): ...


class TaskStatus(BaseModel):
    enabled: int = Field(
        default=0,
        description="啟用的任務數量",
        json_schema_extra={"example": 5},
    )
    disabled: int = Field(
        default=0,
        description="停用的任務數量",
        json_schema_extra={"example": 2},
    )
    model_config = ConfigDict(from_attributes=True)
