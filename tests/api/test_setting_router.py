# tests/api/test_setting_router.py
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from api.main import app
from core import schemas
from core.services.setting import SettingService

client = TestClient(app)


def test_get_all_settings(mocker: MockerFixture):
    """
    測試獲取所有設定的 API 端點。
    """
    # 模擬 SettingService 的 get_all_settings 方法
    mock_settings = {"key1": "value1", "key2": "value2"}
    mocker.patch.object(SettingService, "get_all_settings", return_value=mock_settings)

    response = client.get("/api/v1/settings")
    assert response.status_code == 200
    assert response.json() == mock_settings
    SettingService.get_all_settings.assert_called_once()


def test_get_setting(mocker: MockerFixture):
    """
    測試透過鍵名獲取單一設定的 API 端點。
    """
    mock_setting = schemas.Setting(key="test_key", value="test_value")
    mocker.patch.object(SettingService, "get_setting", return_value=mock_setting)

    response = client.get("/api/v1/setting/test_key")
    assert response.status_code == 200
    assert response.json() == {"key": "test_key", "value": "test_value"}
    SettingService.get_setting.assert_called_once_with("test_key")


def test_update_setting(mocker: MockerFixture):
    """
    測試更新指定設定的 API 端點。
    """
    updated_setting = schemas.Setting(key="test_key", value="new_value")
    mocker.patch.object(SettingService, "update_setting", return_value=updated_setting)

    response = client.put(
        "/api/v1/setting/test_key", json={"value": "new_value"}
    )
    assert response.status_code == 200
    assert response.json() == {"key": "test_key", "value": "new_value"}
    SettingService.update_setting.assert_called_once_with("test_key", "new_value")


def test_update_settings(mocker: MockerFixture):
    """
    測試更新多個設定的 API 端點。
    """
    settings_to_update = {"key1": "value1_new", "key2": "value2_new"}
    updated_settings_list = [
        schemas.Setting(key="key1", value="value1_new"),
        schemas.Setting(key="key2", value="value2_new"),
    ]
    mocker.patch.object(
        SettingService, "update_settings", return_value=updated_settings_list
    )

    response = client.put("/api/v1/settings", json=settings_to_update)
    assert response.status_code == 200
    assert response.json() == settings_to_update
    SettingService.update_settings.assert_called_once_with(settings_to_update)
