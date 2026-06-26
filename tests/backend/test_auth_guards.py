"""require_jwt 與 require_webhook_token 依賴測試。"""

from unittest.mock import MagicMock

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend.dependencies import (
    depends_webhook_token_service,
    require_jwt,
    require_webhook_token,
)
from backend.services.webhook_token_service import WebhookTokenService
from backend.utils.jwt import create_access_token

SECRET = "guard-test-secret"


@pytest.fixture
def jwt_client():
    app = FastAPI()
    app.state.secret_key = SECRET

    @app.get("/api/v1/protected", dependencies=[Depends(require_jwt)])
    def protected():
        return {"ok": True}

    return TestClient(app, raise_server_exceptions=False)


class TestRequireJwt:
    def test_valid_token_passes(self, jwt_client):
        token = create_access_token(SECRET, subject="admin")
        resp = jwt_client.get(
            "/api/v1/protected", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200

    def test_missing_token_401(self, jwt_client):
        assert jwt_client.get("/api/v1/protected").status_code == 401

    def test_invalid_signature_401(self, jwt_client):
        token = create_access_token("other-secret", subject="admin")
        resp = jwt_client.get(
            "/api/v1/protected", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 401

    def test_expired_token_401(self, jwt_client):
        token = create_access_token(SECRET, subject="admin", expires_hours=-1)
        resp = jwt_client.get(
            "/api/v1/protected", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 401

    def test_non_bearer_header_401(self, jwt_client):
        resp = jwt_client.get(
            "/api/v1/protected", headers={"Authorization": "Basic abc"}
        )
        assert resp.status_code == 401


@pytest.fixture
def mock_service():
    return MagicMock(spec=WebhookTokenService)


@pytest.fixture
def webhook_client(mock_service):
    app = FastAPI()

    @app.post("/webhook/on-complete", dependencies=[Depends(require_webhook_token)])
    def hook():
        return {"ok": True}

    app.dependency_overrides[depends_webhook_token_service] = lambda: mock_service
    return TestClient(app, raise_server_exceptions=False), mock_service


class TestRequireWebhookToken:
    def test_no_token_passes_when_none_exist(self, webhook_client):
        client, service = webhook_client
        service.is_enforced.return_value = False
        assert client.post("/webhook/on-complete").status_code == 200

    def test_valid_token_passes_when_enforced(self, webhook_client):
        client, service = webhook_client
        service.is_enforced.return_value = True
        service.verify.return_value = True
        resp = client.post(
            "/webhook/on-complete",
            headers={"Authorization": "Bearer movera_valid"},
        )
        assert resp.status_code == 200

    def test_missing_token_401_when_enforced(self, webhook_client):
        client, service = webhook_client
        service.is_enforced.return_value = True
        assert client.post("/webhook/on-complete").status_code == 401

    def test_invalid_token_401_when_enforced(self, webhook_client):
        client, service = webhook_client
        service.is_enforced.return_value = True
        service.verify.return_value = False
        resp = client.post(
            "/webhook/on-complete",
            headers={"Authorization": "Bearer movera_revoked"},
        )
        assert resp.status_code == 401
