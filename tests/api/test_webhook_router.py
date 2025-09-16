# tests/api/test_webhook_router.py
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from api.main import app

client = TestClient(app)


def test_webhook_status():
    """
    測試 webhook 狀態 API 端點。
    """
    response = client.get("/webhook/status")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "ok"
    assert "available_webhooks" in json_response
    assert len(json_response["available_webhooks"]) > 0


def test_qbittorrent_on_complete(mocker: MockerFixture):
    """
    測試 qBittorrent 下載完成的 webhook API 端點。
    """
    # 模擬 BackgroundTasks.add_task
    mock_add_task = mocker.patch("fastapi.BackgroundTasks.add_task")

    payload = {"filepath": "/downloads/test_file"}
    response = client.post("/webhook/qbittorrent/on-complete", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "code": 200,
        "filepath": "/downloads/test_file",
    }

    # 驗證 process_completed_download 任務被加入到背景任務中
    mock_add_task.assert_called_once()
    # 驗證呼叫 add_task 時的第一個參數是 process_completed_download 函式
    assert mock_add_task.call_args[0][0].__name__ == "process_completed_download"
    # 驗證傳遞給 process_completed_download 的參數是正確的 filepath
    assert mock_add_task.call_args[0][1] == "/downloads/test_file"


def test_qbittorrent_on_complete_invalid_payload():
    """
    測試 qBittorrent webhook API 在收到無效 payload 時的行為。
    """
    # 缺少 'filepath' 欄位
    invalid_payload = {"some_other_key": "some_value"}
    response = client.post("/webhook/qbittorrent/on-complete", json=invalid_payload)

    assert response.status_code == 422  # Unprocessable Entity


def test_qbittorrent_on_complete_exception(mocker: MockerFixture):
    """
    測試當背景任務拋出例外時，API 是否回傳 500 錯誤。
    """
    # 模擬 BackgroundTasks.add_task 拋出例外
    mocker.patch(
        "fastapi.BackgroundTasks.add_task", side_effect=Exception("Task failed")
    )

    payload = {"filepath": "/downloads/test_file"}
    response = client.post("/webhook/qbittorrent/on-complete", json=payload)

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error while processing webhook."}
