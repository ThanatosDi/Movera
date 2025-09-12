from typing import List, Optional

from core.models import Setting
from core.repositories.setting import SettingRepository


class SettingService:
    def __init__(self, repository: SettingRepository):
        self.repository = repository

    def get_all_settings(self) -> List[Setting]:
        """
        獲取所有設定。
        """
        settings = self.repository.get_all()
        result = {setting.key: setting.value for setting in settings}
        return result

    def get_setting(self, key: str) -> Optional[Setting]:
        """
        根據鍵名獲取特定設定。

        :param key: 設定的鍵名。
        """
        return self.repository.get(key)

    def update_setting(
        self, key: str, value: str, description: Optional[str] = None
    ) -> Setting:
        """
        更新或建立一個設定。

        :param key: 設定的鍵名。
        :param value: 設定值。
        :param description: (可選) 設定的描述。
        """
        return self.repository.update(key, value, description)

    def update_settings(self, settings: List[Setting]):
        for setting in settings:
            self.update_setting(setting.key, setting.value, setting.description)
