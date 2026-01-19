"""
SettingService 單元測試
"""

import pytest

from backend.models.setting import Setting
from backend.services.settingService import SettingService


class TestSettingServiceGetAllSettings:
    """測試 SettingService.get_all_settings 方法"""

    def test_get_all_settings_empty(self, setting_service):
        """測試空資料庫取得所有設定"""
        settings = setting_service.get_all_settings()
        assert settings == {}

    def test_get_all_settings_with_settings(self, setting_service, db_session):
        """測試取得所有設定並轉為字典格式"""
        setting1 = Setting(key="timezone", value="Asia/Taipei")
        setting2 = Setting(key="locale", value="zh-TW")
        db_session.add(setting1)
        db_session.add(setting2)
        db_session.commit()

        settings = setting_service.get_all_settings()

        assert isinstance(settings, dict)
        assert settings["timezone"] == "Asia/Taipei"
        assert settings["locale"] == "zh-TW"


class TestSettingServiceGetSettingByKey:
    """測試 SettingService.get_setting_by_key 方法"""

    def test_get_setting_by_key_success(self, setting_service, db_session):
        """測試成功取得單一設定"""
        setting = Setting(key="timezone", value="Asia/Taipei")
        db_session.add(setting)
        db_session.commit()

        found_setting = setting_service.get_setting_by_key("timezone")

        assert found_setting is not None
        assert found_setting.key == "timezone"
        assert found_setting.value == "Asia/Taipei"

    def test_get_setting_by_key_not_found(self, setting_service):
        """測試取得不存在的設定"""
        found_setting = setting_service.get_setting_by_key("non-existent-key")
        assert found_setting is None


class TestSettingServiceUpdateSetting:
    """測試 SettingService.update_setting 方法"""

    def test_update_setting_success(self, setting_service, db_session):
        """測試成功更新設定"""
        setting = Setting(key="timezone", value="Asia/Taipei")
        db_session.add(setting)
        db_session.commit()

        updated_setting = setting_service.update_setting("timezone", "UTC")

        assert updated_setting is not None
        assert updated_setting.value == "UTC"

    def test_update_setting_not_found(self, setting_service):
        """測試更新不存在的設定"""
        updated_setting = setting_service.update_setting("non-existent-key", "value")
        assert updated_setting is None


class TestSettingServiceUpdateSettings:
    """測試 SettingService.update_settings 方法"""

    def test_update_settings_success(self, setting_service, db_session):
        """測試批次更新設定"""
        setting1 = Setting(key="timezone", value="Asia/Taipei")
        setting2 = Setting(key="locale", value="zh-TW")
        db_session.add(setting1)
        db_session.add(setting2)
        db_session.commit()

        settings_data = {
            "timezone": "UTC",
            "locale": "en-US",
        }
        updated_settings = setting_service.update_settings(settings_data)

        assert len(updated_settings) == 2
        # 驗證更新結果
        all_settings = setting_service.get_all_settings()
        assert all_settings["timezone"] == "UTC"
        assert all_settings["locale"] == "en-US"

    def test_update_settings_partial(self, setting_service, db_session):
        """測試批次更新部分存在的設定"""
        setting1 = Setting(key="timezone", value="Asia/Taipei")
        db_session.add(setting1)
        db_session.commit()

        settings_data = {
            "timezone": "UTC",
            "non_existent": "value",  # 這個不存在，會被忽略
        }
        updated_settings = setting_service.update_settings(settings_data)

        assert len(updated_settings) == 1
        all_settings = setting_service.get_all_settings()
        assert all_settings["timezone"] == "UTC"
        assert "non_existent" not in all_settings
