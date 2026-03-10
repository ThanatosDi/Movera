"""
SettingRepository 單元測試
"""

import pytest

from backend.models.setting import Setting
from backend.repositories.setting import SettingRepository


class TestSettingRepositoryGetAll:
    """測試 SettingRepository.get_all 方法"""

    def test_get_all_empty(self, setting_repository):
        """測試空資料庫取得所有設定"""
        settings = setting_repository.get_all()
        assert settings == []

    def test_get_all_with_settings(self, setting_repository, db_session):
        """測試取得所有設定"""
        # 手動建立設定 (因為 SettingRepository 沒有 create 方法)
        setting1 = Setting(key="timezone", value="Asia/Taipei")
        setting2 = Setting(key="locale", value="zh-TW")
        db_session.add(setting1)
        db_session.add(setting2)
        db_session.commit()

        settings = setting_repository.get_all()

        assert len(settings) == 2
        keys = [s.key for s in settings]
        assert "timezone" in keys
        assert "locale" in keys


class TestSettingRepositoryGet:
    """測試 SettingRepository.get 方法"""

    def test_get_success(self, setting_repository, db_session):
        """測試成功取得單一設定"""
        setting = Setting(key="timezone", value="Asia/Taipei")
        db_session.add(setting)
        db_session.commit()

        found_setting = setting_repository.get("timezone")

        assert found_setting is not None
        assert found_setting.key == "timezone"
        assert found_setting.value == "Asia/Taipei"

    def test_get_not_found(self, setting_repository):
        """測試取得不存在的設定"""
        found_setting = setting_repository.get("non-existent-key")
        assert found_setting is None


class TestSettingRepositoryUpdate:
    """測試 SettingRepository.update 方法"""

    def test_update_success(self, setting_repository, db_session):
        """測試成功更新設定"""
        setting = Setting(key="timezone", value="Asia/Taipei")
        db_session.add(setting)
        db_session.commit()

        updated_setting = setting_repository.update("timezone", "UTC")

        assert updated_setting is not None
        assert updated_setting.key == "timezone"
        assert updated_setting.value == "UTC"

    def test_update_not_found(self, setting_repository):
        """測試更新不存在的設定"""
        updated_setting = setting_repository.update("non-existent-key", "value")
        assert updated_setting is None


class TestSettingRepositoryUpdateMany:
    """測試 SettingRepository.update_many 方法"""

    def test_update_many_success(self, setting_repository, db_session):
        """測試批次更新設定"""
        setting1 = Setting(key="timezone", value="Asia/Taipei")
        setting2 = Setting(key="locale", value="zh-TW")
        db_session.add(setting1)
        db_session.add(setting2)
        db_session.commit()

        settings_to_update = {
            "timezone": "UTC",
            "locale": "en-US",
        }
        updated_settings = setting_repository.update_many(settings_to_update)

        assert len(updated_settings) == 2
        # 驗證更新結果
        updated_timezone = setting_repository.get("timezone")
        updated_locale = setting_repository.get("locale")
        assert updated_timezone.value == "UTC"
        assert updated_locale.value == "en-US"

    def test_update_many_partial(self, setting_repository, db_session):
        """測試批次更新部分存在的設定"""
        setting1 = Setting(key="timezone", value="Asia/Taipei")
        db_session.add(setting1)
        db_session.commit()

        settings_to_update = {
            "timezone": "UTC",
            "non_existent": "value",  # 這個不存在
        }
        updated_settings = setting_repository.update_many(settings_to_update)

        # 只有存在的設定會被更新
        assert len(updated_settings) == 1
        assert updated_settings[0].key == "timezone"
        assert updated_settings[0].value == "UTC"

    def test_update_many_empty(self, setting_repository):
        """測試批次更新空字典"""
        updated_settings = setting_repository.update_many({})
        assert updated_settings == []

    def test_update_many_all_not_found(self, setting_repository):
        """測試批次更新全部不存在的設定"""
        settings_to_update = {
            "key1": "value1",
            "key2": "value2",
        }
        updated_settings = setting_repository.update_many(settings_to_update)
        assert updated_settings == []
