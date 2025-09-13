# tests/api/test_log_router.py
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.routers.log import get_log_service
from core.schemas import Log, LogCreate
from core.services.log import LogService

client = TestClient(app)


@pytest.fixture
def mock_log_service():
    mock = MagicMock(spec=LogService)
    return mock


def test_get_logs_for_task(mocker):
    mock_service = MagicMock(spec=LogService)
    mock_service.get_logs_for_task.return_value = [
        Log(
            id=1,
            task_id="test_task",
            level="INFO",
            message="Test log 1",
            timestamp=datetime.now(UTC),
        ),
        Log(
            id=2,
            task_id="test_task",
            level="INFO",
            message="Test log 2",
            timestamp=datetime.now(UTC),
        ),
    ]

    # 正確覆寫依賴：覆寫 get_log_service（而非類別本身）
    app.dependency_overrides[get_log_service] = lambda: mock_service

    response = client.get("/api/v1/log/test_task")

    assert response.status_code == 200
    assert len(response.json()) == 2
    mock_service.get_logs_for_task.assert_called_once_with("test_task")

    app.dependency_overrides = {}


def test_create_log(mocker):
    mock_service = MagicMock(spec=LogService)
    log_create_data = {"task_id": "new_task", "level": "INFO", "message": "New log"}
    log_create = LogCreate(**log_create_data)

    created_log = Log(id=3, **log_create_data, timestamp=datetime.now(UTC))
    mock_service.create_log.return_value = created_log

    app.dependency_overrides[get_log_service] = lambda: mock_service

    response = client.post("/api/v1/log", json=log_create_data)

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["task_id"] == log_create_data["task_id"]
    assert response_data["message"] == log_create_data["message"]
    mock_service.create_log.assert_called_once()

    app.dependency_overrides = {}
