from typing import Literal, Optional

from pydantic import BaseModel, Field, create_model


class SettingBase(BaseModel):
    key: str = Field(..., description="設定名稱", example="timezone")
    value: str = Field(..., description="設定值", example="Asia/Taipei")
    description: Optional[str] = Field(None, description="設定描述", example="時區設定")


class SettingUpdate(BaseModel):
    value: str = Field(..., description="設定值", example="Asia/Taipei")
    description: Optional[str] = Field(None, description="設定描述", example="時區設定")


class Setting(SettingBase): ...
