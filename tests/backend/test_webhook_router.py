"""
Webhook Router 單元測試
"""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from backend.routers.webhook import router


@pytest.fixture
def app():
    """建立測試用的 FastAPI app"""
    app = FastAPI()
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """建立測試用的 TestClient"""
    return TestClient(app)


class TestWebhookStatus:
    """測試 /webhook/status 端點"""

    def test_webhook_status_success(self, client):
        """測試成功取得 webhook 狀態"""
        response = client.get("/webhook/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "timestamp" in data
        assert "available_webhooks" in data

    def test_webhook_status_available_webhooks(self, client):
        """測試可用的 webhook 端點列表"""
        response = client.get("/webhook/status")

        data = response.json()
        webhooks = data["available_webhooks"]
        assert len(webhooks) >= 1

        # 檢查 qbittorrent webhook
        qb_webhook = next(
            (w for w in webhooks if "qbittorrent" in w["path"]), None
        )
        assert qb_webhook is not None
        assert qb_webhook["method"] == "POST"


class TestDownloaderOnComplete:
    """測試 /webhook/on-complete 和 /webhook/qbittorrent/on-complete 端點"""

    @patch("backend.routers.webhook.process_completed_download")
    def test_on_complete_success(self, mock_process, client):
        """測試成功觸發 webhook"""
        payload = {"filepath": "/downloads/test.mp4"}

        response = client.post("/webhook/on-complete", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["code"] == 200
        assert data["filepath"] == "/downloads/test.mp4"

    @patch("backend.routers.webhook.process_completed_download")
    def test_qbittorrent_on_complete_success(self, mock_process, client):
        """測試 qbittorrent 端點成功觸發 webhook"""
        payload = {"filepath": "/downloads/test.mp4"}

        response = client.post("/webhook/qbittorrent/on-complete", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_on_complete_missing_filepath(self, client):
        """測試缺少 filepath 欄位"""
        payload = {}

        response = client.post("/webhook/on-complete", json=payload)

        assert response.status_code == 422  # Validation Error

    def test_on_complete_with_optional_fields(self, client):
        """測試帶有可選欄位的 payload"""
        with patch("backend.routers.webhook.process_completed_download"):
            payload = {
                "filepath": "/downloads/test.mp4",
                "category": "anime",
                "tags": "1080p,webrip",
            }

            response = client.post("/webhook/on-complete", json=payload)

            assert response.status_code == 200

    @patch("backend.routers.webhook.process_completed_download")
    def test_on_complete_background_task(self, mock_process, client):
        """測試背景任務被正確加入"""
        payload = {"filepath": "/downloads/test.mp4"}

        response = client.post("/webhook/on-complete", json=payload)

        # 由於使用 BackgroundTasks，函數會被呼叫但不會立即執行
        assert response.status_code == 200

    def test_on_complete_invalid_json(self, client):
        """測試無效的 JSON"""
        response = client.post(
            "/webhook/on-complete",
            content="invalid json",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 422
