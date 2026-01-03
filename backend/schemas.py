from datetime import UTC, datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

# --- Base Configuration ---


class OrmBaseModel(BaseModel):
    """A base model with ORM mode enabled using Pydantic v2's config."""

    model_config = {"from_attributes": True}


# --- Log Schemas ---


class LogBase(BaseModel):
    task_id: str = Field(
        ...,
        description="任務的 ID",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"},
    )
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        ...,
        description="日誌的等級",
        examples=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    message: str = Field(..., description="日誌的內容訊息", examples=[""])
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="日誌的建立時間",
        examples=["2023-10-01 12:00:00"],
    )


class LogCreate(LogBase):
    pass


class Log(LogBase, OrmBaseModel):
    id: int


# --- Task Schemas ---


class TaskUUID(BaseModel):
    id: str = Field(
        ...,
        description="自動產生的任務 ID，為 UUID 格式",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )


class TaskBase(BaseModel):
    name: str = Field(..., description="任務的名稱", examples=["公爵千金的家庭教師"])
    include: str = Field(
        ..., description="用於匹配檔案的包含規則", examples=["公爵千金的家庭教師"]
    )
    move_to: str = Field(
        ...,
        description="檔案移動到的目標目錄路徑",
        examples=["/Downloads/anime/公爵千金的家庭教師"],
    )
    src_filename: Optional[str] = Field(None, description="來源檔案名稱規則")
    dst_filename: Optional[str] = Field(None, description="目標檔案名稱模板")
    rename_rule: Optional[Literal["regex", "parse"]] = Field(
        None, description="重新命名規則的類型"
    )
    enabled: bool = Field(True, description="任務的啟用狀態")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class Task(TaskBase, TaskUUID, OrmBaseModel):
    created_at: datetime = Field(
        description="任務的建立時間",
    )
    logs: List[Log] = []  # 包含關聯的 logs


class TaskStats(BaseModel):
    enabled: int = 0
    disabled: int = 0


# --- Setting Schemas ---


class SettingBase(BaseModel):
    key: str = Field(
        ..., description="設定名稱", json_schema_extra={"example": "timezone"}
    )
    value: str = Field(
        ..., description="設定值", json_schema_extra={"example": "Asia/Taipei"}
    )


class SettingUpdate(BaseModel):
    value: str = Field(
        ..., description="設定值", json_schema_extra={"example": "Asia/Taipei"}
    )


class Setting(SettingBase, OrmBaseModel):
    pass


# --- WebSocket Schemas ---


class WebSocketMessage(BaseModel):
    """對應前端傳來的正規化 WebSocket 訊息結構。"""

    event: str
    payload: Optional[dict[str, str | bool | None]] = None
    requestId: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


# --- Parse Preview Schemas ---


class ParsePreviewRequest(BaseModel):
    src_pattern: str = Field(
        ...,
        description="用於解析的模式字串",
        json_schema_extra={
            "example": "{en_title} - {cht_title} - {episode} {tags}.mp4"
        },
    )
    text: str = Field(
        ...,
        description="要被解析的文字",
        json_schema_extra={
            "example": "Neko ni Tensei Shita Ojisan S02 - 轉生為第七王子，隨心所欲的魔法學習之路 第二季 - 13 [1080P][Baha][WEB-DL][AAC AVC][CHT].mp4"
        },
    )
    dst_pattern: str = Field(
        ...,
        description="用於產生新字串的格式化字串",
        json_schema_extra={
            "example": "{en_title} - {cht_title} - S02E{episode} {tags}.mp4"
        },
    )


class ParsePreviewResponse(ParsePreviewRequest):
    groups: dict[str, str | int | float] = Field(
        ...,
        description="解析後的分組結果",
        json_schema_extra={
            "example": {
                "en_title": "Neko ni Tensei Shita Ojisan S02",
                "cht_title": "轉生為第七王子，隨心所欲的魔法學習之路 第二季",
                "episode": "13",
                "tags": "[1080P][Baha][WEB-DL][AAC AVC][CHT]",
            }
        },
    )
    formatted: str = Field(
        ...,
        description="格式化後的預覽結果",
        json_schema_extra={
            "example": "Neko ni Tensei Shita Ojisan S02 - 轉生為第七王子，隨心所欲的魔法學習之路 第二季 - S02E13 [1080P][Baha][WEB-DL][AAC AVC][CHT].mp4"
        },
    )


class RegexPreviewRequest(BaseModel):
    src_pattern: str = Field(
        ...,
        description="用於解析的模式字串",
        json_schema_extra={"example": "(\\w+) - (\\d{2})(v2)? .+\\.mp4"},
    )
    text: str = Field(
        ...,
        description="要被解析的文字",
        json_schema_extra={
            "example": "公爵千金的家庭教師 - 01 [1080P][WEB-DL][AAC AVC][CHT].mp4"
        },
    )
    dst_pattern: str = Field(
        ...,
        description="用於產生新字串的格式化字串",
        json_schema_extra={
            "example": "\\1 - S01E\\2 [1080P][WEB-DL][AAC AVC][CHT].mp4"
        },
    )


class RegexPreviewResponse(RegexPreviewRequest):
    groups: list[str | None] = Field(
        ...,
        description="解析後的分組結果",
        json_schema_extra={"example": ["公爵千金的家庭教師", "01", None]},
    )
    formatted: str = Field(
        ...,
        description="格式化後的預覽結果",
        json_schema_extra={
            "example": "公爵千金的家庭教師 - S01E01 [1080P][WEB-DL][AAC AVC][CHT].mp4"
        },
    )


# --- Webhook Schemas ---


class DownloaderOnCompletePayload(BaseModel):
    """qBittorrent 'run external program' 的資料模型。"""

    filepath: str = Field(..., description="下載的內容路徑")
    category: Optional[str] = Field(None, description="種子的類別")
    tags: Optional[str] = Field(None, description="種子的標籤")
