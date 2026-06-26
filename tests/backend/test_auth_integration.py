"""端到端整合測試：以真實 app 驗證 登入 → 存取 API → webhook token → webhook 強制。

使用 StaticPool 的共享 in-memory SQLite，讓 TestClient 的工作執行緒與測試共用同一個資料庫。
不進入 TestClient context manager，以避免觸發 lifespan（alembic 遷移與帳號 seed）。
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import backend.models  # noqa: F401  確保所有 model 註冊到 Base
from backend.backend import app
from backend.database import Base
from backend.dependencies import get_db
from backend.utils.security import sha256_hex


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("MOVERA_SECRET_KEY", raising=False)
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(Engine, "connect")
    def _fk(dbapi_con, _):
        dbapi_con.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)

    def _get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db
    app.state.secret_key = "integration-test-secret-key-0123456789abcdef"
    c = TestClient(app, raise_server_exceptions=False)
    yield c
    app.dependency_overrides.clear()


def test_full_auth_flow(client):
    # 1. 初始狀態：需要初始化設定
    assert client.get("/api/v1/auth/status").json()["needs_setup"] is True

    # 2. 未登入存取受保護 API → 401
    assert client.get("/api/v1/tags").status_code == 401

    # 3. 初始化建立帳號並取得 token
    setup = client.post(
        "/api/v1/auth/setup", json={"username": "admin", "password": sha256_hex("pw")}
    )
    assert setup.status_code == 200
    token = setup.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 4. 帶 token 存取受保護 API → 200
    assert client.get("/api/v1/tags", headers=headers).status_code == 200

    # 5. status 變為不需設定；重複登入可行
    assert client.get("/api/v1/auth/status").json()["needs_setup"] is False
    login = client.post(
        "/api/v1/auth/login", json={"username": "admin", "password": sha256_hex("pw")}
    )
    assert login.status_code == 200


def test_webhook_compatibility_then_enforced(client):
    # webhook token 管理需要登入
    setup = client.post(
        "/api/v1/auth/setup", json={"username": "admin", "password": sha256_hex("pw")}
    )
    headers = {"Authorization": f"Bearer {setup.json()['access_token']}"}

    # 尚無 token：webhook 放行
    r = client.post("/webhook/on-complete", json={"filepath": "/downloads/a.mp4"})
    assert r.status_code == 200

    # 建立 webhook token（取得一次性明文）
    created = client.post(
        "/api/v1/webhook-tokens", json={"name": "qb"}, headers=headers
    )
    assert created.status_code == 201
    movera_token = created.json()["token"]
    assert movera_token.startswith("movera_")

    # 現在強制：未帶 token → 401
    assert (
        client.post(
            "/webhook/on-complete", json={"filepath": "/downloads/a.mp4"}
        ).status_code
        == 401
    )

    # 帶合法 token → 200
    ok = client.post(
        "/webhook/on-complete",
        json={"filepath": "/downloads/a.mp4"},
        headers={"Authorization": f"Bearer {movera_token}"},
    )
    assert ok.status_code == 200
