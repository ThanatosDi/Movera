"""
Setting Router 單元測試
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from fastapi.exceptions import ResponseValidationError

from backend.routers.setting import router
from backend.models.setting import Setting
from backend.services.settingService import SettingService


@pytest.fixture
def mock_setting_service():
    """建立 mock 的 SettingService"""
    return MagicMock(spec=SettingService)


@pytest.fixture
def app(mock_setting_service):
    """建立測試用的 FastAPI app"""
    from backend.dependencies import depends_setting_service

    app = FastAPI()
    app.include_router(router)

    # 覆寫依賴注入
    app.dependency_overrides[depends_setting_service] = lambda: mock_setting_service

    return app


@pytest.fixture
def client(app):
    """建立測試用的 TestClient (不拋出 server exceptions)"""
    return TestClient(app, raise_server_exceptions=False)


class TestGetAllSettings:
    """測試 GET /api/v1/settings 端點"""

    def test_get_all_settings_empty(self, client, mock_setting_service):
        """測試取得空設定"""
        mock_setting_service.get_all_settings.return_value = {}

        response = client.get("/api/v1/settings")

        assert response.status_code == 200
        assert response.json() == {}

    def test_get_all_settings_with_settings(self, client, mock_setting_service):
        """測試取得所有設定"""
        mock_setting_service.get_all_settings.return_value = {
            "timezone": "Asia/Taipei",
            "locale": "zh-TW",
        }

        response = client.get("/api/v1/settings")

        assert response.status_code == 200
        data = response.json()
        assert data["timezone"] == "Asia/Taipei"
        assert data["locale"] == "zh-TW"


class TestGetSetting:
    """測試 GET /api/v1/setting/{key} 端點"""

    def test_get_setting_success(self, client, mock_setting_service):
        """測試成功取得單一設定"""
        mock_setting = MagicMock()
        mock_setting.key = "timezone"
        mock_setting.value = "Asia/Taipei"
        mock_setting_service.get_setting_by_key.return_value = mock_setting

        response = client.get("/api/v1/setting/timezone")

        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "timezone"
        assert data["value"] == "Asia/Taipei"

    def test_get_setting_not_found(self, client, mock_setting_service):
        """測試取得不存在的設定

        注意：目前 API 沒有處理 None 的情況，會導致 ResponseValidationError。
        這是 API 設計上的問題，應該回傳 404 而非讓驗證失敗。
        此測試驗證目前的實際行為（500 錯誤）。
        """
        mock_setting_service.get_setting_by_key.return_value = None

        response = client.get("/api/v1/setting/non-existent-key")

        # 當 service 回傳 None 時，FastAPI 的 response_model 驗證會失敗
        # 這會導致 500 Internal Server Error
        assert response.status_code == 500


class TestUpdateSetting:
    """測試 PUT /api/v1/setting/{key} 端點"""

    def test_update_setting_success(self, client, mock_setting_service):
        """測試成功更新設定"""
        mock_setting = MagicMock()
        mock_setting.key = "timezone"
        mock_setting.value = "UTC"
        mock_setting_service.update_setting.return_value = mock_setting

        response = client.put(
            "/api/v1/setting/timezone",
            json={"value": "UTC"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["key"] == "timezone"
        assert data["value"] == "UTC"

    def test_update_setting_not_found(self, client, mock_setting_service):
        """測試更新不存在的設定

        注意：目前 API 沒有處理 None 的情況，會導致 ResponseValidationError。
        這是 API 設計上的問題，應該回傳 404 而非讓驗證失敗。
        此測試驗證目前的實際行為（500 錯誤）。
        """
        mock_setting_service.update_setting.return_value = None

        response = client.put(
            "/api/v1/setting/non-existent-key",
            json={"value": "some-value"},
        )

        # 當 service 回傳 None 時，FastAPI 的 response_model 驗證會失敗
        # 這會導致 500 Internal Server Error
        assert response.status_code == 500

    def test_update_setting_invalid_payload(self, client, mock_setting_service):
        """測試無效的 payload"""
        response = client.put(
            "/api/v1/setting/timezone",
            json={},  # 缺少 value
        )

        assert response.status_code == 422


class TestUpdateSettings:
    """測試 PUT /api/v1/settings 端點"""

    def test_update_settings_success(self, client, mock_setting_service):
        """測試批次更新設定"""
        mock_settings = [
            MagicMock(key="timezone", value="UTC"),
            MagicMock(key="locale", value="en-US"),
        ]
        mock_setting_service.update_settings.return_value = mock_settings

        response = client.put(
            "/api/v1/settings",
            json={"timezone": "UTC", "locale": "en-US"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["timezone"] == "UTC"
        assert data["locale"] == "en-US"

    def test_update_settings_partial(self, client, mock_setting_service):
        """測試部分更新成功"""
        mock_settings = [MagicMock(key="timezone", value="UTC")]
        mock_setting_service.update_settings.return_value = mock_settings

        response = client.put(
            "/api/v1/settings",
            json={"timezone": "UTC", "non_existent": "value"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["timezone"] == "UTC"
        assert "non_existent" not in data

    def test_update_settings_empty(self, client, mock_setting_service):
        """測試空的更新請求"""
        mock_setting_service.update_settings.return_value = []

        response = client.put(
            "/api/v1/settings",
            json={},
        )

        assert response.status_code == 200
        assert response.json() == {}
