from datetime import datetime, UTC

from pydantic import BaseModel, Field


class LogBase(BaseModel):
    task_id: str
    level: str
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class LogCreate(LogBase):
    pass


class Log(LogBase):
    id: int

    model_config = {"from_attributes": True}
