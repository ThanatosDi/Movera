"""
Task Router 批量端點單元測試
"""

from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from backend.exceptions.task_exception import TaskAlreadyExists, TaskNotFound
from backend.models.task import Task
from backend.routers.task import router
from backend.services.task_service import TaskService


@pytest.fixture
def mock_task_service():
    return MagicMock(spec=TaskService)


@pytest.fixture
def app(mock_task_service):
    from backend.dependencies import depends_task_service

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[depends_task_service] = lambda: mock_task_service

    @app.exception_handler(TaskNotFound)
    async def _task_not_found(request, exc):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(TaskAlreadyExists)
    async def _task_already_exists(request, exc):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    return app


@pytest.fixture
def client(app):
    return TestClient(app, raise_server_exceptions=False)


def _make_task(id="task-1", name="任務", enabled=True):
    t = Task()
    t.id = id
    t.name = name
    t.include = "關鍵字"
    t.move_to = "/downloads/test"
    t.src_filename = None
    t.dst_filename = None
    t.rename_rule = None
    t.episode_offset_enabled = False
    t.episode_offset_group = None
    t.episode_offset_value = 0
    t.enabled = enabled
    t.created_at = datetime.now(UTC)
    t.tags = []
    t.logs = []
    return t


class TestBatchCreateRouter:
    def test_batch_create_success(self, client, mock_task_service):
        mock_task_service.batch_create_tasks.return_value = [
            _make_task(id="1", name="A"),
            _make_task(id="2", name="B"),
        ]
        payload = {
            "items": [
                {
                    "name": "A",
                    "include": "關鍵字",
                    "move_to": "/downloads/a",
                },
                {
                    "name": "B",
                    "include": "關鍵字",
                    "move_to": "/downloads/b",
                },
            ]
        }
        response = client.post("/api/v1/tasks/batch", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert len(data["items"]) == 2
        assert data["items"][0]["name"] == "A"

    def test_batch_create_conflict(self, client, mock_task_service):
        mock_task_service.batch_create_tasks.side_effect = TaskAlreadyExists("A")
        payload = {
            "items": [
                {"name": "A", "include": "x", "move_to": "/y"},
            ]
        }
        response = client.post("/api/v1/tasks/batch", json=payload)
        assert response.status_code == 409

    def test_batch_create_empty_items(self, client, mock_task_service):
        response = client.post("/api/v1/tasks/batch", json={"items": []})
        assert response.status_code == 400

    def test_batch_create_over_limit(self, client, mock_task_service):
        items = [
            {"name": f"t{i}", "include": "x", "move_to": "/y"} for i in range(501)
        ]
        response = client.post("/api/v1/tasks/batch", json={"items": items})
        assert response.status_code == 400


class TestBatchUpdateRouter:
    def test_batch_update_enabled_success(self, client, mock_task_service):
        mock_task_service.batch_update_tasks.return_value = [
            _make_task(id="1", name="A", enabled=False),
            _make_task(id="2", name="B", enabled=False),
        ]
        payload = {
            "items": [
                {"id": "1", "patch": {"enabled": False}},
                {"id": "2", "patch": {"enabled": False}},
            ]
        }
        response = client.put("/api/v1/tasks/batch", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert all(item["enabled"] is False for item in data["items"])

    def test_batch_update_not_found(self, client, mock_task_service):
        mock_task_service.batch_update_tasks.side_effect = TaskNotFound("missing-id")
        payload = {"items": [{"id": "missing-id", "patch": {"enabled": True}}]}
        response = client.put("/api/v1/tasks/batch", json=payload)
        assert response.status_code == 404

    def test_batch_update_name_conflict(self, client, mock_task_service):
        mock_task_service.batch_update_tasks.side_effect = TaskAlreadyExists("Dup")
        payload = {
            "items": [
                {"id": "1", "patch": {"name": "Dup"}},
                {"id": "2", "patch": {"name": "Dup"}},
            ]
        }
        response = client.put("/api/v1/tasks/batch", json=payload)
        assert response.status_code == 409

    def test_batch_update_empty_items(self, client):
        response = client.put("/api/v1/tasks/batch", json={"items": []})
        assert response.status_code == 400


class TestBatchDeleteRouter:
    def test_batch_delete_success(self, client, mock_task_service):
        mock_task_service.batch_delete_tasks.return_value = ["1", "2"]
        response = client.request(
            "DELETE", "/api/v1/tasks/batch", json={"ids": ["1", "2"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["deleted_ids"] == ["1", "2"]

    def test_batch_delete_not_found(self, client, mock_task_service):
        mock_task_service.batch_delete_tasks.side_effect = TaskNotFound("missing")
        response = client.request(
            "DELETE", "/api/v1/tasks/batch", json={"ids": ["missing"]}
        )
        assert response.status_code == 404

    def test_batch_delete_empty_ids(self, client):
        response = client.request(
            "DELETE", "/api/v1/tasks/batch", json={"ids": []}
        )
        assert response.status_code == 400
