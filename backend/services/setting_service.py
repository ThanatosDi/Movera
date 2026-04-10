import json

from backend import models, schemas
from backend.repositories.setting import SettingRepository
from backend.utils.logger import logger
from backend.utils.path_validator import validate_allowed_directories


class SettingService:
    """Read/write application settings with JSON-field serialisation.

    Why: Settings include both plain-string and JSON-list values (e.g.
    allowed_directories). This service owns the serialisation boundary so
    that repositories and routers never deal with JSON encoding details.
    """

    def __init__(self, repository: SettingRepository):
        self.repository = repository

    # 需要特殊序列化/反序列化的 JSON 欄位
    _JSON_FIELDS = {"allowed_directories"}

    def get_all_settings(self) -> dict:
        """Return every setting as a plain dict, deserialising JSON fields.

        Why: JSON-list settings (e.g. allowed_directories) are stored as strings
        in the database but the API must return them as native lists so the
        frontend can consume them without extra parsing.
        """
        settings = self.repository.get_all()
        result: dict = {}
        for setting in settings:
            if setting.key in self._JSON_FIELDS:
                try:
                    result[setting.key] = json.loads(setting.value)
                except (json.JSONDecodeError, TypeError):
                    result[setting.key] = []
            else:
                result[setting.key] = setting.value
        return result

    def get_setting_by_key(self, key: str) -> models.Setting | None:
        return self.repository.get(key)

    def update_setting(self, key: str, value: str) -> models.Setting | None:
        return self.repository.update(key, value)

    def update_settings(self, settings_data: dict) -> list[models.Setting]:
        """Bulk-update settings, serialising JSON fields and validating paths.

        Why: The frontend sends a mixed bag of plain strings and list values
        in one request. This method splits them so plain fields go through a
        fast batch update while JSON fields are individually validated
        (e.g. absolute-path check for allowed_directories) and serialised.

        Raises:
            ValueError: If allowed_directories contains non-absolute paths.
        """
        # 分離 JSON 欄位和普通字串欄位
        json_fields = {}
        str_fields = {}
        for key, value in settings_data.items():
            if key in self._JSON_FIELDS:
                json_fields[key] = value
            else:
                str_fields[key] = value

        # 更新普通字串欄位
        updated = self.repository.update_many(str_fields) if str_fields else []

        # JSON 欄位使用 create_or_update（序列化為 JSON 字串）
        for key, value in json_fields.items():
            if key == "allowed_directories" and isinstance(value, list):
                invalid = validate_allowed_directories(value)
                if invalid:
                    raise ValueError(
                        f"允許目錄僅接受絕對路徑，以下路徑無效: {', '.join(invalid)}"
                    )
            json_value = json.dumps(value) if not isinstance(value, str) else value
            setting = self.repository.create_or_update(key, json_value)
            updated.append(setting)

        return updated

    def get_allowed_directories(self) -> list[str]:
        """Return the list of allowed directory paths, defaulting to ``[]``.

        Why: Multiple callers (DirectoryService, path validation) need the
        parsed list. Centralising the deserialisation and fallback logic here
        prevents each caller from repeating JSON-decode error handling.
        """
        setting = self.repository.get("allowed_directories")
        if setting is None:
            return []
        try:
            dirs = json.loads(setting.value)
            if isinstance(dirs, list):
                return dirs
            return []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_allowed_directories(self, directories: list[str]) -> None:
        invalid = validate_allowed_directories(directories)
        if invalid:
            raise ValueError(
                f"允許目錄僅接受絕對路徑，以下路徑無效: {', '.join(invalid)}"
            )
        self.repository.create_or_update(
            "allowed_directories", json.dumps(directories)
        )
