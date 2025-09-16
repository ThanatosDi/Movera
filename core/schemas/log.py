from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


class LogBase(BaseModel):
    task_id: str = Field(
        ...,
        description="任務的 ID",
        json_schema_extra={"example": "123e4567-e89b-12d3-a456-426614174000"},
    )
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        ...,
        description="日誌的等級，例如 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'",
        examples=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    message: str = Field(
        ...,
        description="日誌的內容訊息",
        examples=[""],
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="日誌的建立時間",
        examples=["2023-10-01 12:00:00"],
    )


class LogCreate(LogBase):
    pass


class Log(LogBase):
    id: int

    model_config = {"from_attributes": True}
