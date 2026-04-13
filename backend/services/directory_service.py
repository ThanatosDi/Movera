from pathlib import Path

from backend.exceptions.directory_exception import (
    DirectoryAccessDenied,
    DirectoryNotFound,
)
from backend.services.setting_service import SettingService


class DirectoryService:
    """在管理者允許的目錄範圍內瀏覽檔案系統。

    Why: 前端直接存取檔案系統會有安全風險。
    此服務透過白名單機制，確保使用者只能看到設定中明確允許的目錄。
    """

    def __init__(self, setting_service: SettingService):
        self.setting_service = setting_service

    def list_directories(self, path: str | None) -> list[dict]:
        """回傳 *path* 的子目錄清單，若 *path* 為 None 則回傳允許的根目錄清單。

        Why: 前端樹狀檢視需要根目錄列表（允許的目錄）和子目錄展開功能；
        此方法同時處理兩種情境，並強制執行存取控制。

        Raises:
            DirectoryNotFound: *path* 指向的目錄不存在。
            DirectoryAccessDenied: *path* 不在任何允許的目錄範圍內。
        """
        allowed = self.setting_service.get_allowed_directories()

        if path is None:
            return self._list_root_directories(allowed)

        self._validate_path_access(path, allowed)

        resolved = Path(path).resolve()
        if not resolved.is_dir():
            raise DirectoryNotFound(path)

        return self._scan_directories(resolved)

    def _list_root_directories(self, allowed: list[str]) -> list[dict]:
        result = []
        for dir_path in allowed:
            resolved = Path(dir_path).resolve()
            if resolved.is_dir():
                result.append({
                    "name": resolved.name,
                    "path": str(resolved),
                    "has_children": self._has_subdirectories(resolved),
                })
        return result

    def _validate_path_access(self, path: str, allowed: list[str]) -> None:
        resolved = Path(path).resolve()
        for allowed_dir in allowed:
            allowed_resolved = Path(allowed_dir).resolve()
            if resolved == allowed_resolved or self._is_subpath(resolved, allowed_resolved):
                return
        raise DirectoryAccessDenied(path)

    def _is_subpath(self, path: Path, parent: Path) -> bool:
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_hidden_directory(name: str) -> bool:
        """檢查目錄名稱是否為隱藏或系統目錄（.、#、@ 開頭）。"""
        return name.startswith((".", "#", "@"))

    def _scan_directories(self, path: Path) -> list[dict]:
        result = []
        try:
            for entry in sorted(path.iterdir()):
                if entry.is_dir() and not entry.is_symlink() and not self._is_hidden_directory(entry.name):
                    result.append({
                        "name": entry.name,
                        "path": str(entry),
                        "has_children": self._has_subdirectories(entry),
                    })
        except PermissionError:
            pass
        return result

    def _has_subdirectories(self, path: Path) -> bool:
        try:
            for entry in path.iterdir():
                if entry.is_dir() and not entry.is_symlink() and not self._is_hidden_directory(entry.name):
                    return True
        except PermissionError:
            pass
        return False
