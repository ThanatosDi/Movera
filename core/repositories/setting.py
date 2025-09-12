from typing import List, Optional

from sqlalchemy.orm import Session

from core import models, schemas
from core.database import get_db

# TODO: 確定 SettingRepository 是否正確

class SettingRepository:
    def __init__(self, db: Session = next(get_db())):
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

    def update(
        self, key: str, value: str, description: Optional[str] = None
    ) -> Optional[models.Setting]:
        """
        更新或建立一個設定項目。

        如果指定的鍵名存在，則更新其值和描述；
        如果不存在，則建立一個新的設定項目。

        :param key: 要更新或建立的設定的鍵名。
        :param value: 新的設定值。
        :param description: (可選) 設定的描述。
        :return: 更新或建立後的設定項目。
        """
        setting = self.get(key)
        if setting:
            # 更新現有設定
            setting.value = value
            if description is not None:
                setting.description = description
        else:
            # 建立新設定
            setting = schemas.SettingUpdate(
                key=key, value=value, description=description
            )
            self.db.add(setting)

        self.db.commit()
        self.db.refresh(setting)
        return setting
