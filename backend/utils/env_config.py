"""環境變數設定解析模組。

Why: Docker 部署環境中需要透過環境變數預先配置目錄白名單，
此模組負責解析環境變數並過濾出有效的絕對路徑。
"""

import os

from backend.utils.path_validator import is_absolute_path


def _parse_comma_separated_paths(env_key: str) -> list[str]:
    """解析逗號分隔的環境變數為絕對路徑陣列，忽略相對路徑。"""
    raw = os.getenv(env_key, "")
    if not raw.strip():
        return []
    paths = [p.strip() for p in raw.split(",") if p.strip()]
    return [p for p in paths if is_absolute_path(p)]


def get_env_allowed_directories() -> list[str]:
    """從環境變數 ALLOWED_DIRECTORIES 取得允許目錄清單。"""
    return _parse_comma_separated_paths("ALLOWED_DIRECTORIES")


def get_env_allowed_source_directories() -> list[str]:
    """從環境變數 ALLOWED_SOURCE_DIRECTORIES 取得允許來源目錄清單。"""
    return _parse_comma_separated_paths("ALLOWED_SOURCE_DIRECTORIES")


def get_allow_webui_setting() -> bool:
    """從環境變數 ALLOW_WEBUI_SETTING 取得是否允許前端修改目錄設定。

    預設為 True（允許）。設為 'false'（大小寫不敏感）時回傳 False。
    """
    return os.getenv("ALLOW_WEBUI_SETTING", "true").lower() != "false"
