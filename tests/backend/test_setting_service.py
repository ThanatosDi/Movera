"""
SettingService 單元測試
"""

import json

import pytest

from backend.models.setting import Setting
from backend.services.setting_service import SettingService


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


class TestSettingServiceAllowedDirectories:
    """測試 SettingService 的 allowed_directories 相關方法"""

    def test_get_allowed_directories_default_empty(self, setting_service):
        """測試未設定時回傳空陣列"""
        result = setting_service.get_allowed_directories()
        assert result == []

    def test_get_allowed_directories_with_data(self, setting_service, db_session):
        """測試已設定時回傳路徑列表"""
        dirs = ["/downloads", "/media"]
        setting = Setting(
            key="allowed_directories", value=json.dumps(dirs)
        )
        db_session.add(setting)
        db_session.commit()

        result = setting_service.get_allowed_directories()
        assert result == ["/downloads", "/media"]

    def test_set_allowed_directories(self, setting_service, db_session):
        """測試更新 allowed_directories 為 JSON 路徑陣列"""
        # 先建立 setting
        setting = Setting(key="allowed_directories", value="[]")
        db_session.add(setting)
        db_session.commit()

        dirs = ["/downloads/anime", "/media/movies"]
        setting_service.set_allowed_directories(dirs)

        result = setting_service.get_allowed_directories()
        assert result == ["/downloads/anime", "/media/movies"]

    def test_set_allowed_directories_creates_if_not_exists(self, setting_service, db_session):
        """測試若設定不存在時自動建立"""
        dirs = ["/downloads"]
        setting_service.set_allowed_directories(dirs)

        result = setting_service.get_allowed_directories()
        assert result == ["/downloads"]

    def test_allowed_directories_schema_validation(self, setting_service, db_session):
        """測試 allowed_directories 值為無效 JSON 時回傳空陣列"""
        setting = Setting(key="allowed_directories", value="not-valid-json")
        db_session.add(setting)
        db_session.commit()

        result = setting_service.get_allowed_directories()
        assert result == []

    def test_get_all_settings_deserializes_allowed_directories(self, setting_service, db_session):
        """測試 get_all_settings 回傳時 allowed_directories 已反序列化為 list"""
        setting1 = Setting(key="timezone", value="Asia/Taipei")
        setting2 = Setting(key="allowed_directories", value=json.dumps(["/downloads", "/media"]))
        db_session.add(setting1)
        db_session.add(setting2)
        db_session.commit()

        result = setting_service.get_all_settings()
        assert result["timezone"] == "Asia/Taipei"
        assert result["allowed_directories"] == ["/downloads", "/media"]
        assert isinstance(result["allowed_directories"], list)

    def test_update_settings_with_allowed_directories(self, setting_service, db_session):
        """測試 update_settings 可同時處理字串欄位和 JSON 欄位"""
        setting = Setting(key="timezone", value="Asia/Taipei")
        db_session.add(setting)
        db_session.commit()

        settings_data = {
            "timezone": "UTC",
            "allowed_directories": ["/downloads", "/media"],
        }
        setting_service.update_settings(settings_data)

        result = setting_service.get_all_settings()
        assert result["timezone"] == "UTC"
        assert result["allowed_directories"] == ["/downloads", "/media"]

    def test_update_settings_creates_allowed_directories(self, setting_service, db_session):
        """測試 update_settings 可建立不存在的 allowed_directories"""
        settings_data = {
            "allowed_directories": ["/new/path"],
        }
        setting_service.update_settings(settings_data)

        result = setting_service.get_allowed_directories()
        assert result == ["/new/path"]


class TestSettingServiceAllowedDirectoriesValidation:
    """測試 allowed_directories 絕對路徑驗證"""

    def test_set_allowed_directories_accepts_posix_absolute(self, setting_service):
        """測試接受 POSIX 絕對路徑"""
        setting_service.set_allowed_directories(["/downloads", "/media/movies"])
        assert setting_service.get_allowed_directories() == ["/downloads", "/media/movies"]

    def test_set_allowed_directories_accepts_windows_absolute(self, setting_service):
        """測試接受 Windows 絕對路徑"""
        setting_service.set_allowed_directories(["C:\\Downloads", "D:/Media"])
        assert setting_service.get_allowed_directories() == ["C:\\Downloads", "D:/Media"]

    def test_set_allowed_directories_rejects_relative_path(self, setting_service):
        """測試拒絕相對路徑"""
        with pytest.raises(ValueError, match="僅接受絕對路徑"):
            setting_service.set_allowed_directories(["downloads/anime"])

    def test_set_allowed_directories_rejects_dot_relative(self, setting_service):
        """測試拒絕 ./ 和 ../ 開頭的相對路徑"""
        with pytest.raises(ValueError, match="僅接受絕對路徑"):
            setting_service.set_allowed_directories(["./downloads"])

        with pytest.raises(ValueError, match="僅接受絕對路徑"):
            setting_service.set_allowed_directories(["../escape"])

    def test_set_allowed_directories_rejects_mixed(self, setting_service):
        """測試混合路徑中有相對路徑時拒絕全部"""
        with pytest.raises(ValueError, match="relative/path"):
            setting_service.set_allowed_directories(["/valid/path", "relative/path"])

    def test_update_settings_rejects_relative_allowed_directories(self, setting_service):
        """測試透過 update_settings 也會驗證"""
        with pytest.raises(ValueError, match="僅接受絕對路徑"):
            setting_service.update_settings({
                "allowed_directories": ["not/absolute"],
            })
