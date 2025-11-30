from typing import List, Optional

from sqlalchemy.orm import Session

from backend import models


class SettingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[models.Setting]:
        """
        獲取所有設定項目。

        :return: 所有設定項目的列表。
        """
        return self.db.query(models.Setting).all()

    def get(self, key: str) -> Optional[models.Setting]:
        """
        根據鍵名獲取單一設定項目。

        :param key: 設定的鍵名。
        :return: 對應的設定項目，如果不存在則返回 None。
        """
        return self.db.query(models.Setting).filter(models.Setting.key == key).first()

    def update(self, key: str, value: str) -> Optional[models.Setting]:
        """
        更新一個設定項目。

        如果指定的鍵名存在，則更新其值；如果不存在，則不進行任何操作。

        :param key: 要更新的設定的鍵名。
        :param value: 新的設定值。
        :return: 更新後的設定項目；如果鍵名不存在，則返回 None。
        """
        setting = self.get(key)
        if setting:
            # 僅當設定存在時才更新
            setting.value = value
            self.db.commit()
            self.db.refresh(setting)
            return setting
        # 如果 setting 不存在，返回 None
        return None

    def update_many(self, settings_to_update: dict[str, str]) -> List[models.Setting]:
        """
        批次更新多個設定項目。

        只會更新字典中鍵名已經存在於資料庫的項目。
        不存在的鍵名將會被忽略。

        :param settings_to_update: 一個包含 {key: value} 的字典。
        :return: 成功更新的設定項目列表。
        """
        # 查詢出所有待更新的、且存在於資料庫中的 setting 物件
        settings_in_db = (
            self.db.query(models.Setting)
            .filter(models.Setting.key.in_(settings_to_update.keys()))
            .all()
        )

        updated_settings = []
        for setting in settings_in_db:
            # 從傳入的字典中取得新值並更新物件
            new_value = settings_to_update.get(setting.key)
            if new_value is not None:
                setting.value = new_value
                updated_settings.append(setting)

        # 如果有任何項目被更新，則一次性提交
        if updated_settings:
            self.db.commit()

        return updated_settings
