from backend import models, schemas
from backend.repositories.setting import SettingRepository
from backend.utils.logger import logger


class SettingService:
    def __init__(self, repository: SettingRepository):
        self.repository = repository

    def get_all_settings(self) -> dict[str, str]:
        settings = self.repository.get_all()
        result = {setting.key: setting.value for setting in settings}
        return result

    def get_setting_by_key(self, key: str) -> models.Setting | None:
        return self.repository.get(key)

    def update_setting(self, key: str, value: str) -> models.Setting | None:
        return self.repository.update(key, value)

    def update_settings(self, settings_data: dict[str, str]):
        return self.repository.update_many(settings_data)
