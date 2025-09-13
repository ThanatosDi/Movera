# tests/api/test_task_router.py
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.routers.task import get_task_service
from core.schemas import Task, TaskCreate, TaskStats, TaskUpdate
from core.services.task import TaskService

client = TestClient(app)


@pytest.fixture
def mock_task_service():
    mock = MagicMock(spec=TaskService)
    return mock


def test_get_all_tasks(mocker):
    mock_service = MagicMock(spec=TaskService)
    mock_service.get_all_tasks.return_value = [
        Task(
            id="1",
            name="Task 1",
            include="*.txt",
            move_to="/dest",
            created_at=datetime.now(UTC),
        ),
        Task(
            id="2",
            name="Task 2",
            include="*.jpg",
            move_to="/dest2",
            created_at=datetime.now(UTC),
        ),
    ]

    # 正確覆寫依賴：覆寫 get_task_service（而非類別本身）
    app.dependency_overrides[get_task_service] = lambda: mock_service

    response = client.get("/api/v1/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 2
    mock_service.get_all_tasks.assert_called_once()

    app.dependency_overrides = {}


def test_create_task(mocker):
    mock_service = MagicMock(spec=TaskService)
    task_create_data = {"name": "New Task", "include": "*.csv", "move_to": "/new_dest"}
    task_create = TaskCreate(**task_create_data)

    created_task = Task(id="3", **task_create_data, created_at=datetime.now(UTC))
    mock_service.create_task.return_value = created_task

    app.dependency_overrides[get_task_service] = lambda: mock_service

    response = client.post("/api/v1/task", json=task_create_data)

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["name"] == task_create_data["name"]
    mock_service.create_task.assert_called_once()

    app.dependency_overrides = {}


def test_update_task(mocker):
    mock_service = MagicMock(spec=TaskService)
    task_update_data = {
        "name": "Updated Task",
        "include": "*.doc",
        "move_to": "/updated_dest",
    }
    task_update = TaskUpdate(**task_update_data)

    updated_task = Task(id="1", **task_update_data, created_at=datetime.now(UTC))
    mock_service.update_task.return_value = updated_task

    app.dependency_overrides[get_task_service] = lambda: mock_service

    response = client.put("/api/v1/task/1", json=task_update_data)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data["name"] == task_update_data["name"]
    mock_service.update_task.assert_called_once_with("1", mocker.ANY)

    app.dependency_overrides = {}


def test_delete_task(mocker):
    mock_service = MagicMock(spec=TaskService)
    mock_service.delete_task.return_value = None

    app.dependency_overrides[get_task_service] = lambda: mock_service

    response = client.delete("/api/v1/task/1")

    assert response.status_code == 204
    mock_service.delete_task.assert_called_once_with("1")

    app.dependency_overrides = {}


def test_get_task_stats(mocker):
    mock_service = MagicMock(spec=TaskService)
    mock_service.get_task_stats.return_value = TaskStats(enabled=5, disabled=2)

    app.dependency_overrides[get_task_service] = lambda: mock_service

    response = client.get("/api/v1/tasks/stats")

    assert response.status_code == 200
    assert response.json() == {"enabled": 5, "disabled": 2}
    mock_service.get_task_stats.assert_called_once()

    app.dependency_overrides = {}
