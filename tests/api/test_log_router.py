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


import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from api.main import app
from api.routers.log import get_log_service
from core.repositories.log import LogRepository
from core.schemas import Log, LogCreate
from core.services.log import LogService

client = TestClient(app)


@pytest.fixture
def mock_log_repo(mocker: MockerFixture) -> MagicMock:
    return mocker.MagicMock(spec=LogRepository)


def test_get_logs_for_task(mocker: MockerFixture, mock_log_repo: MagicMock):
    mock_log_repo.get_by_task_id.return_value = [
        Log(
            id=1,
            task_id="test_task",
            level="INFO",
            message="Test log 1",
            timestamp=datetime.now(UTC),
        ),
    ]

    # 覆寫 get_db 來回傳一個帶有 mock repo 的 session
    mocker.patch("api.routers.log.get_db", return_value=mocker.MagicMock())
    mocker.patch("api.routers.log.LogRepository", return_value=mock_log_repo)

    response = client.get("/api/v1/log/test_task")

    assert response.status_code == 200
    assert len(response.json()) == 1
    mock_log_repo.get_by_task_id.assert_called_once_with("test_task")


def test_create_log(mocker: MockerFixture, mock_log_repo: MagicMock):
    log_create_data = {"task_id": "new_task", "level": "INFO", "message": "New log"}
    log_create = LogCreate(**log_create_data)

    # 模擬 create 方法
    mock_log_repo.create.return_value = Log(
        id=3, **log_create_data, timestamp=datetime.now(UTC)
    )

    mocker.patch("api.routers.log.get_db", return_value=mocker.MagicMock())
    mocker.patch("api.routers.log.LogRepository", return_value=mock_log_repo)
    mock_print = mocker.patch("builtins.print")

    response = client.post("/api/v1/log", json=log_create_data)

    assert response.status_code == 201
    response_data = response.json()
    assert response_data["task_id"] == log_create_data["task_id"]

    mock_log_repo.create.assert_called_once()
    mock_print.assert_called_once_with(mocker.ANY)


def test_get_logs_for_task_no_logs(mocker: MockerFixture, mock_log_repo: MagicMock):
    """
    測試當任務沒有日誌時，API 端點應回傳空列表。
    """
    mock_log_repo.get_by_task_id.return_value = []

    mocker.patch("api.routers.log.get_db", return_value=mocker.MagicMock())
    mocker.patch("api.routers.log.LogRepository", return_value=mock_log_repo)

    response = client.get("/api/v1/log/task_with_no_logs")

    assert response.status_code == 200
    assert response.json() == []
    mock_log_repo.get_by_task_id.assert_called_once_with("task_with_no_logs")
