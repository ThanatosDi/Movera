from typing import Literal, Optional

from pydantic import BaseModel, Field


class SettingBase(BaseModel):
    key: str = Field(..., description="設定名稱")
    value: str = Field(..., description="設定值")
    description: Optional[str] = Field(None, description="設定描述")


class SettingUpdate(SettingBase): ...


class Setting(SettingBase): ...
