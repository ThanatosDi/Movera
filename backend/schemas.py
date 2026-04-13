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
    message: str = Field(..., max_length=5000, description="日誌的內容訊息", examples=[""])
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
    name: str = Field(..., max_length=255, description="任務的名稱", examples=["公爵千金的家庭教師"])
    include: str = Field(
        ..., max_length=1000, description="用於匹配檔案的包含規則", examples=["公爵千金的家庭教師"]
    )
    move_to: str = Field(
        ...,
        max_length=4096,
        description="檔案移動到的目標目錄路徑",
        examples=["/Downloads/anime/公爵千金的家庭教師"],
    )
    src_filename: Optional[str] = Field(None, max_length=1000, description="來源檔案名稱規則")
    dst_filename: Optional[str] = Field(None, max_length=1000, description="目標檔案名稱模板")
    rename_rule: Optional[Literal["regex", "parse"]] = Field(
        None, description="重新命名規則的類型"
    )
    enabled: bool = Field(True, description="任務的啟用狀態")


class TaskCreate(TaskBase):
    tag_ids: List[str] = Field(default_factory=list, description="關聯的標籤 ID 列表")


class TaskUpdate(TaskBase):
    tag_ids: List[str] = Field(default_factory=list, description="關聯的標籤 ID 列表")


class Task(TaskBase, TaskUUID, OrmBaseModel):
    created_at: datetime = Field(
        description="任務的建立時間",
    )
    logs: List[Log] = []  # 包含關聯的 logs
    tags: List["Tag_"] = Field(default_factory=list, description="關聯的標籤")


class TaskStats(BaseModel):
    enabled: int = 0
    disabled: int = 0


# --- Tag Schemas ---

ALLOWED_TAG_COLORS = {"red", "orange", "yellow", "green", "blue", "purple", "pink", "gray"}


class TagBase(BaseModel):
    name: str = Field(..., max_length=255, description="標籤名稱", examples=["動畫"])
    color: str = Field(..., max_length=20, description="標籤顏色（預定義色票名稱）", examples=["blue"])


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    pass


class Tag_(TagBase, OrmBaseModel):
    id: str = Field(
        ...,
        description="自動產生的標籤 ID，為 UUID 格式",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    created_at: datetime = Field(
        description="標籤的建立時間",
    )


# --- Preset Rule Schemas ---

ALLOWED_RULE_TYPES = {"parse", "regex"}
ALLOWED_FIELD_TYPES = {"src", "dst"}


class PresetRuleBase(BaseModel):
    name: str = Field(..., max_length=255, description="常用規則名稱", examples=["動畫季番命名"])
    rule_type: Literal["parse", "regex"] = Field(..., description="規則引擎類型", examples=["parse"])
    field_type: Literal["src", "dst"] = Field(..., description="對應欄位類型", examples=["src"])
    pattern: str = Field(..., max_length=1000, description="規則內容", examples=["{title} - {episode}.mp4"])


class PresetRuleCreate(PresetRuleBase):
    pass


class PresetRuleUpdate(PresetRuleBase):
    pass


class PresetRule_(PresetRuleBase, OrmBaseModel):
    id: str = Field(
        ...,
        description="自動產生的常用規則 ID，為 UUID 格式",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    created_at: datetime = Field(
        description="常用規則的建立時間",
    )


# --- Setting Schemas ---


class SettingBase(BaseModel):
    key: str = Field(
        ..., max_length=255, description="設定名稱", json_schema_extra={"example": "timezone"}
    )
    value: str = Field(
        ..., max_length=5000, description="設定值", json_schema_extra={"example": "Asia/Taipei"}
    )


class SettingUpdate(BaseModel):
    value: str = Field(
        ..., max_length=5000, description="設定值", json_schema_extra={"example": "Asia/Taipei"}
    )


class Setting(SettingBase, OrmBaseModel):
    pass


# --- Parse Preview Schemas ---


class ParsePreviewRequest(BaseModel):
    src_pattern: str = Field(
        ...,
        max_length=1000,
        description="用於解析的模式字串",
        json_schema_extra={
            "example": "{en_title} - {cht_title} - {episode} {tags}.mp4"
        },
    )
    text: str = Field(
        ...,
        max_length=1000,
        description="要被解析的文字",
        json_schema_extra={
            "example": "Neko ni Tensei Shita Ojisan S02 - 轉生為第七王子，隨心所欲的魔法學習之路 第二季 - 13 [1080P][Baha][WEB-DL][AAC AVC][CHT].mp4"
        },
    )
    dst_pattern: str = Field(
        ...,
        max_length=1000,
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
        max_length=1000,
        description="用於解析的模式字串",
        json_schema_extra={"example": "(\\w+) - (\\d{2})(v2)? .+\\.mp4"},
    )
    text: str = Field(
        ...,
        max_length=1000,
        description="要被解析的文字",
        json_schema_extra={
            "example": "公爵千金的家庭教師 - 01 [1080P][WEB-DL][AAC AVC][CHT].mp4"
        },
    )
    dst_pattern: str = Field(
        ...,
        max_length=1000,
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


# --- Directory Schemas ---


class DirectoryItem(BaseModel):
    name: str = Field(..., description="目錄名稱", examples=["anime"])
    path: str = Field(
        ..., description="完整路徑", examples=["/downloads/anime"]
    )
    has_children: bool = Field(
        ..., description="是否有子目錄", examples=[True]
    )


class DirectoryListResponse(BaseModel):
    directories: List[DirectoryItem] = Field(
        default_factory=list, description="目錄列表"
    )


# --- Webhook Schemas ---


class DownloaderOnCompletePayload(BaseModel):
    """qBittorrent 'run external program' 的資料模型。"""

    filepath: str = Field(..., max_length=4096, description="下載的內容路徑")
    category: Optional[str] = Field(None, max_length=255, description="種子的類別")
    tags: Optional[str] = Field(None, max_length=255, description="種子的標籤")
