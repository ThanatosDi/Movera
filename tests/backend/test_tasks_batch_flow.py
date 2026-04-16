"""
批量 Task API 整合測試：建立 → 更新 → 刪除 完整流程

使用自己的 in-memory SQLite（StaticPool）讓 FastAPI TestClient 在不同 thread
中仍能看到同一個 DB。
"""

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.dependencies import depends_task_service
from backend.exceptions.task_exception import TaskAlreadyExists, TaskNotFound
from backend.repositories.task import TaskRepository
from backend.routers.task import router
from backend.services.task_service import TaskService


@pytest.fixture
def integration_engine():
    """使用 StaticPool 讓所有連線共用同一個 in-memory DB。"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def integration_session_factory(integration_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=integration_engine)


@pytest.fixture
def app(integration_session_factory):
    fastapi_app = FastAPI()
    fastapi_app.include_router(router)

    def _service_override():
        session = integration_session_factory()
        try:
            repo = TaskRepository(db=session)
            yield TaskService(repository=repo)
        finally:
            session.close()

    fastapi_app.dependency_overrides[depends_task_service] = _service_override

    @fastapi_app.exception_handler(TaskNotFound)
    async def _task_not_found(request, exc):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @fastapi_app.exception_handler(TaskAlreadyExists)
    async def _task_already_exists(request, exc):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    return fastapi_app


@pytest.fixture
def client(app):
    return TestClient(app, raise_server_exceptions=True)


def test_batch_create_update_delete_flow(client):
    """完整流程：批量建立 3 筆 → 批量停用 3 筆 → 批量刪除 3 筆"""
    # 1. 批量建立
    create_payload = {
        "items": [
            {"name": f"任務{i}", "include": "kw", "move_to": f"/d/{i}"}
            for i in range(1, 4)
        ]
    }
    r = client.post("/api/v1/tasks/batch", json=create_payload)
    assert r.status_code == 201
    created = r.json()["items"]
    assert len(created) == 3
    ids = [t["id"] for t in created]
    assert all(t["enabled"] is True for t in created)

    # 2. 批量停用
    update_payload = {
        "items": [{"id": tid, "patch": {"enabled": False}} for tid in ids]
    }
    r = client.put("/api/v1/tasks/batch", json=update_payload)
    assert r.status_code == 200
    updated = r.json()["items"]
    assert len(updated) == 3
    assert all(t["enabled"] is False for t in updated)

    # 3. 批量刪除
    r = client.request(
        "DELETE", "/api/v1/tasks/batch", json={"ids": ids}
    )
    assert r.status_code == 200
    assert set(r.json()["deleted_ids"]) == set(ids)

    # 驗證全部消失
    r = client.get("/api/v1/tasks")
    assert r.status_code == 200
    assert r.json() == []


def test_batch_create_rollback_on_duplicate(client):
    """批量建立遇到重名時整體 rollback"""
    # 先建立 1 筆
    r = client.post(
        "/api/v1/tasks/batch",
        json={"items": [{"name": "A", "include": "x", "move_to": "/a"}]},
    )
    assert r.status_code == 201

    # 第二批中含重名
    r = client.post(
        "/api/v1/tasks/batch",
        json={
            "items": [
                {"name": "B", "include": "x", "move_to": "/b"},
                {"name": "A", "include": "x", "move_to": "/a2"},
            ]
        },
    )
    assert r.status_code == 409

    # 此時 DB 應只有 A 一筆
    r = client.get("/api/v1/tasks")
    assert r.status_code == 200
    tasks = r.json()
    assert len(tasks) == 1
    assert tasks[0]["name"] == "A"


def test_batch_update_rollback_on_missing_id(client):
    """批量更新遇到不存在 id 時整體 rollback"""
    r = client.post(
        "/api/v1/tasks/batch",
        json={"items": [{"name": "A", "include": "x", "move_to": "/a"}]},
    )
    assert r.status_code == 201
    existing_id = r.json()["items"][0]["id"]

    # 批量更新：一筆存在、一筆不存在
    r = client.put(
        "/api/v1/tasks/batch",
        json={
            "items": [
                {"id": existing_id, "patch": {"enabled": False}},
                {"id": "non-existent", "patch": {"enabled": False}},
            ]
        },
    )
    assert r.status_code == 404

    # 存在的那筆不應被修改
    r = client.get(f"/api/v1/tasks/{existing_id}")
    assert r.status_code == 200
    assert r.json()["enabled"] is True


def test_batch_delete_rollback_on_missing_id(client):
    """批量刪除遇到不存在 id 時整體 rollback"""
    r = client.post(
        "/api/v1/tasks/batch",
        json={"items": [{"name": "A", "include": "x", "move_to": "/a"}]},
    )
    existing_id = r.json()["items"][0]["id"]

    r = client.request(
        "DELETE",
        "/api/v1/tasks/batch",
        json={"ids": [existing_id, "non-existent"]},
    )
    assert r.status_code == 404

    # 存在的那筆仍存在
    r = client.get(f"/api/v1/tasks/{existing_id}")
    assert r.status_code == 200
