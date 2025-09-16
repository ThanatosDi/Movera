# api/schemas/task.py
import uuid
from datetime import UTC, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class TaskUUID(BaseModel):
    id: uuid.UUID = Field(
        ...,
        description="自動產生的任務 ID，為 UUID 格式，用於唯一標識每個任務。",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )


class TaskBase(BaseModel):
    name: str = Field(
        ...,
        description="任務的名稱，用於描述任務的目的或功能。",
        examples=["公爵千金的家庭教師"],
    )
    include: str = Field(
        ...,
        description="用於匹配檔案的包含規則，通常是檔案名稱或路徑中的關鍵字。",
        examples=["公爵千金的家庭教師"],
    )
    move_to: str = Field(
        ...,
        description="檔案匹配任務後，將檔案移動到的目標目錄路徑。",
        examples=["/Downloads/anime/公爵千金的家庭教師"],
    )
    src_filename: Optional[str] = Field(
        None,
        description="用於匹配檔案的包含規則，通常是檔案名稱或路徑中的關鍵字。",
        examples=[
            "(.+公爵千金的家庭教師 - )(\\d{2})( .+)\\.mp4",
            "[{fansub}]{title} - {episode} {tags}.mp4",
        ],
    )
    dst_filename: Optional[str] = Field(
        None,
        description="用於重新命名檔案的目標名稱模板，支援字串解析或正則表達式替換。",
        examples=[
            "\\1S01E\\2\\3.mp4",
            "[{fansub}]{title} - S01E{episode} {tags}.mp4",
        ],
    )
    rename_rule: Optional[Literal["regex", "parse"]] = Field(
        None,
        description="指定重新命名規則的類型，支援 'regex' (正則表達式) 或 'parse' (字串解析)。",
        examples=["regex", "parse"],
    )
    enabled: bool = Field(
        True,
        description="任務的啟用狀態，True 表示任務啟用，False 表示任務禁用。",
        examples=[True, False],
    )


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    pass


class Task(TaskBase, TaskUUID):
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="任務的建立時間，表示任務何時被創建。",
        examples=["2023-10-01 12:00:00"],
    )

    model_config = {"from_attributes": True}


class TaskStats(BaseModel):
    enabled: int = 0
    disabled: int = 0
