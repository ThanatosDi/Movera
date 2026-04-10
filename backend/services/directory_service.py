from pathlib import Path

from backend.exceptions.directory_exception import (
    DirectoryAccessDenied,
    DirectoryNotFound,
)
from backend.services.setting_service import SettingService


class DirectoryService:
    """Browse the filesystem within administrator-allowed directories.

    Why: Direct filesystem access from the frontend would be a security risk.
    This service enforces an allow-list so users can only see directories
    explicitly permitted in settings.
    """

    def __init__(self, setting_service: SettingService):
        self.setting_service = setting_service

    def list_directories(self, path: str | None) -> list[dict]:
        """Return child directories for *path*, or the allowed root list when *path* is None.

        Why: The frontend tree-view needs both a root listing (allowed dirs)
        and drill-down into sub-directories; this single method handles both
        cases while enforcing access control.

        Raises:
            DirectoryNotFound: *path* does not point to an existing directory.
            DirectoryAccessDenied: *path* is outside every allowed directory.
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

    def _scan_directories(self, path: Path) -> list[dict]:
        result = []
        try:
            for entry in sorted(path.iterdir()):
                if entry.is_dir() and not entry.name.startswith("."):
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
                if entry.is_dir() and not entry.name.startswith("."):
                    return True
        except PermissionError:
            pass
        return False
