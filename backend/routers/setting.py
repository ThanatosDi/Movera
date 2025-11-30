from fastapi import APIRouter, Depends

from backend.services.settingService import SettingService

from .. import schemas
from ..dependencies import depends_setting_service

router = APIRouter(prefix="/api/v1", tags=["Settings"])


@router.get(
    "/settings",
    response_model=dict[str, str],
    summary="獲取所有設定",
    response_description="所有設定的列表",
)
def get_all_settings(service: SettingService = Depends(depends_setting_service)):
    """
    獲取資料庫中所有設定的完整列表。

    這個 API 用於查詢系統中存在的所有設定，並返回一個包含設定物件的陣列。

    回應內容:
    - `key`: 設定的唯一鍵名
    - `value`: 設定的值
    """
    return service.get_all_settings()


@router.get(
    "/setting/{key}",
    response_model=schemas.Setting,
    summary="透過鍵名獲取設定",
    response_description="具有指定鍵名的設定物件。",
)
def get_setting(key: str, service: SettingService = Depends(depends_setting_service)):
    """
    透過鍵名獲取資料庫中指定的設定。

    這個 API 用於查詢系統中存在的特定設定，並返回一個設定物件。

    回應內容:
    - `key`: 設定的唯一鍵名
    - `value`: 設定的值
    """
    return service.get_setting_by_key(key)


@router.put(
    "/setting/{key}",
    response_model=schemas.Setting,
    summary="更新指定設定",
    response_description="成功更新後的設定資訊",
)
def update_setting(
    key: str,
    setting: schemas.SettingUpdate,
    service: SettingService = Depends(depends_setting_service),
):
    """
    根據鍵名更新現有的設定。

    這個 API 允許使用者修改設定的值和描述。

    回應內容:
    - `key`: 設定的唯一鍵名
    - `value`: 設定的值
    """
    return service.update_setting(key, setting.value)


@router.put(
    "/settings",
    response_model=dict[str, str],
    summary="更新多個設定",
    response_description="成功更新後的設定資訊",
)
def update_settings(
    settings: dict[str, str],
    service: SettingService = Depends(depends_setting_service),
):
    updated_settings = service.update_settings(settings)
    # 將更新成功的 Setting 物件列表轉換為 key: value 的字典格式回傳
    return {setting.key: setting.value for setting in updated_settings}
