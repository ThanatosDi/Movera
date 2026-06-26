"""Auth Router 測試：status / setup / login（service 以 mock 注入）。"""

from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.dependencies import depends_auth_service
from backend.routers.auth import router
from backend.services.auth_service import AuthService
from backend.utils.security import sha256_hex


@pytest.fixture
def mock_auth_service():
    return MagicMock(spec=AuthService)


@pytest.fixture
def app(mock_auth_service):
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[depends_auth_service] = lambda: mock_auth_service
    return app


@pytest.fixture
def client(app):
    return TestClient(app, raise_server_exceptions=False)


class TestAuthStatus:
    def test_status_needs_setup_true(self, client, mock_auth_service):
        mock_auth_service.needs_setup.return_value = True
        resp = client.get("/api/v1/auth/status")
        assert resp.status_code == 200
        assert resp.json()["needs_setup"] is True

    def test_status_needs_setup_false(self, client, mock_auth_service):
        mock_auth_service.needs_setup.return_value = False
        resp = client.get("/api/v1/auth/status")
        assert resp.json()["needs_setup"] is False


class TestSetup:
    def test_setup_creates_account_and_returns_token(self, client, mock_auth_service):
        mock_auth_service.needs_setup.return_value = True
        mock_auth_service.issue_token.return_value = "jwt-token"
        resp = client.post(
            "/api/v1/auth/setup",
            json={"username": "admin", "password": sha256_hex("p")},
        )
        assert resp.status_code == 200
        assert resp.json()["access_token"] == "jwt-token"
        mock_auth_service.create_admin.assert_called_once()

    def test_setup_rejected_when_account_exists(self, client, mock_auth_service):
        mock_auth_service.needs_setup.return_value = False
        resp = client.post(
            "/api/v1/auth/setup",
            json={"username": "x", "password": sha256_hex("y")},
        )
        assert resp.status_code == 409
        mock_auth_service.create_admin.assert_not_called()


class TestLogin:
    def test_login_success(self, client, mock_auth_service):
        mock_auth_service.verify_credentials.return_value = True
        mock_auth_service.issue_token.return_value = "jwt-token"
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": sha256_hex("secret")},
        )
        assert resp.status_code == 200
        assert resp.json()["access_token"] == "jwt-token"

    def test_login_wrong_password(self, client, mock_auth_service):
        mock_auth_service.verify_credentials.return_value = False
        resp = client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": sha256_hex("wrong")},
        )
        assert resp.status_code == 401

    def test_login_sends_hashed_not_plaintext(self, client, mock_auth_service):
        # 契約：前端送的是 sha256 值（不等於明文），後端以該值驗證
        mock_auth_service.verify_credentials.return_value = True
        mock_auth_service.issue_token.return_value = "jwt-token"
        hashed = sha256_hex("secret")
        assert hashed != "secret"
        client.post("/api/v1/auth/login", json={"username": "admin", "password": hashed})
        mock_auth_service.verify_credentials.assert_called_once_with("admin", hashed)
