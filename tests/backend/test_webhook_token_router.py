"""Webhook Token Router 測試：list / create / revoke（service 以 mock 注入）。"""

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.dependencies import depends_webhook_token_service
from backend.models.webhook_token import WebhookToken
from backend.routers.webhook_token import router
from backend.services.webhook_token_service import WebhookTokenService


def _make_token(id="tok-1", name="qb", revoked_at=None):
    t = WebhookToken()
    t.id = id
    t.name = name
    t.token_hash = "hash"
    t.created_at = datetime.now(UTC)
    t.revoked_at = revoked_at
    return t


@pytest.fixture
def mock_service():
    return MagicMock(spec=WebhookTokenService)


@pytest.fixture
def app(mock_service):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[depends_webhook_token_service] = lambda: mock_service
    return app


@pytest.fixture
def client(app):
    return TestClient(app, raise_server_exceptions=False)


class TestWebhookTokenRouter:
    def test_create_returns_plaintext_token(self, client, mock_service):
        mock_service.create_token.return_value = ("movera_secret123", _make_token())
        resp = client.post("/api/v1/webhook-tokens", json={"name": "qb"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["token"] == "movera_secret123"
        assert data["name"] == "qb"
        assert data["revoked_at"] is None

    def test_list_omits_plaintext(self, client, mock_service):
        mock_service.list_tokens.return_value = [_make_token()]
        resp = client.get("/api/v1/webhook-tokens")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        assert "token" not in items[0]
        assert items[0]["name"] == "qb"

    def test_revoke_token(self, client, mock_service):
        mock_service.revoke_token.return_value = _make_token(
            revoked_at=datetime.now(UTC)
        )
        resp = client.delete("/api/v1/webhook-tokens/tok-1")
        assert resp.status_code == 204

    def test_revoke_unknown_returns_404(self, client, mock_service):
        mock_service.revoke_token.return_value = None
        resp = client.delete("/api/v1/webhook-tokens/nope")
        assert resp.status_code == 404

    def test_delete_revoked_token(self, client, mock_service):
        mock_service.get_token.return_value = _make_token(
            revoked_at=datetime.now(UTC)
        )
        mock_service.delete_token.return_value = True
        resp = client.delete("/api/v1/webhook-tokens/tok-1/permanent")
        assert resp.status_code == 204
        mock_service.delete_token.assert_called_once_with("tok-1")

    def test_delete_unknown_returns_404(self, client, mock_service):
        mock_service.get_token.return_value = None
        resp = client.delete("/api/v1/webhook-tokens/nope/permanent")
        assert resp.status_code == 404

    def test_delete_active_token_rejected_409(self, client, mock_service):
        mock_service.get_token.return_value = _make_token(revoked_at=None)
        resp = client.delete("/api/v1/webhook-tokens/tok-1/permanent")
        assert resp.status_code == 409
        mock_service.delete_token.assert_not_called()
