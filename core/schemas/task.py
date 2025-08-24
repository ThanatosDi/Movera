# api/schemas/task.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TaskBase(BaseModel):
    name: str
    include: str
    move_to: str
    src_filename: Optional[str] = None
    dst_filename: Optional[str] = None
    rename_rule: Optional[str] = None
    enabled: bool = True

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    pass

class Task(TaskBase):
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}

class TaskStats(BaseModel):
    enabled: int = 0
    disabled: int = 0
