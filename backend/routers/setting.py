from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from backend.services.setting_service import SettingService
from backend.utils.env_config import get_allow_webui_setting

from .. import schemas
from ..dependencies import depends_setting_service

_LOCKED_DIRECTORY_KEYS = {"allowed_directories", "allowed_source_directories"}

# 允許透過 PUT /api/v1/settings 修改的 key 白名單。
# 新增設定項時需同步更新此清單。
_ALLOWED_SETTING_KEYS = {"timezone", "locale", "allowed_directories", "allowed_source_directories"}

router = APIRouter(prefix="/api/v1", tags=["Settings"])


@router.get(
    "/settings",
    summary="獲取所有設定",
    response_description="所有設定的列表",
)
def get_all_settings(service: SettingService = Depends(depends_setting_service)):
    """
    獲取資料庫中所有設定的完整列表。

    這個 API 用於查詢系統中存在的所有設定，並返回一個包含設定物件的陣列。

    回應內容:
    - `key`: 設定的唯一鍵名
    - `value`: 設定的值（JSON 欄位會自動反序列化）
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
    summary="更新多個設定",
    response_description="成功更新後的設定資訊",
)
def update_settings(
    settings: dict,
    service: SettingService = Depends(depends_setting_service),
):
    # 過濾掉不在白名單內的 key
    settings = {k: v for k, v in settings.items() if k in _ALLOWED_SETTING_KEYS}

    # ALLOW_WEBUI_SETTING=false 時拒絕修改目錄設定
    if not get_allow_webui_setting():
        if _LOCKED_DIRECTORY_KEYS & settings.keys():
            raise HTTPException(
                status_code=403,
                detail="目錄設定已被管理者鎖定，無法透過 Web UI 修改",
            )

    try:
        service.update_settings(settings)
    except ValueError as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})
    # 回傳完整的最新設定（含 JSON 反序列化）
    return service.get_all_settings()
