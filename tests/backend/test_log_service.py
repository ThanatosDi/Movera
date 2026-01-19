"""
LogService 單元測試
"""

import pytest

from backend import schemas
from backend.services.logService import LogService


class TestLogServiceGetLogsByTaskId:
    """測試 LogService.get_logs_by_task_id 方法"""

    def test_get_logs_by_task_id_success(
        self, log_service, task_service, sample_task_data
    ):
        """測試成功取得任務的日誌"""
        task = task_service.create_task(schemas.TaskCreate(**sample_task_data))

        # 建立多筆日誌
        for i in range(3):
            log_service.create_log(
                schemas.LogCreate(task_id=task.id, level="INFO", message=f"日誌 {i}")
            )

        logs = log_service.get_logs_by_task_id(task.id)

        assert len(logs) == 3

    def test_get_logs_by_task_id_empty(self, log_service, task_service, sample_task_data):
        """測試取得沒有日誌的任務"""
        task = task_service.create_task(schemas.TaskCreate(**sample_task_data))

        logs = log_service.get_logs_by_task_id(task.id)

        assert logs == []

    def test_get_logs_by_task_id_not_found(self, log_service):
        """測試取得不存在任務的日誌"""
        logs = log_service.get_logs_by_task_id("non-existent-task-id")
        assert logs == []


class TestLogServiceCreateLog:
    """測試 LogService.create_log 方法"""

    def test_create_log_success(self, log_service, task_service, sample_task_data):
        """測試成功建立日誌"""
        task = task_service.create_task(schemas.TaskCreate(**sample_task_data))

        log = log_service.create_log(
            schemas.LogCreate(task_id=task.id, level="INFO", message="測試訊息")
        )

        assert log is not None
        assert log.id is not None
        assert log.task_id == task.id
        assert log.level == "INFO"
        assert log.message == "測試訊息"

    def test_create_log_with_all_levels(
        self, log_service, task_service, sample_task_data
    ):
        """測試建立不同等級的日誌"""
        task = task_service.create_task(schemas.TaskCreate(**sample_task_data))

        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in levels:
            log = log_service.create_log(
                schemas.LogCreate(task_id=task.id, level=level, message=f"{level} 訊息")
            )
            assert log.level == level
