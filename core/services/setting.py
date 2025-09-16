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

    def update_setting(self, key: str, value: str) -> Setting:
        """
        更新或建立一個設定。

        :param key: 設定的鍵名。
        :param value: 設定值。
        """
        return self.repository.update(key, value)

    def update_settings(self, settings_data: dict[str, str]) -> List[Setting]:
        """
        批量更新多個設定。

        使用 repository 的 update_many 方法來高效處理。
        只會更新鍵名存在於資料庫中的設定。

        :param settings_data: 一個包含 {key: value} 的字典。
        :return: 成功更新的 Setting 物件列表。
        """
        return self.repository.update_many(settings_data)
