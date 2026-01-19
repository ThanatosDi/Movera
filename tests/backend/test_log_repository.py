"""
LogRepository 單元測試
"""

import pytest
from datetime import datetime, UTC

from backend import schemas
from backend.repositories.log import LogRepository


class TestLogRepositoryCreate:
    """測試 LogRepository.create 方法"""

    def test_create_log_success(self, log_repository, task_repository, sample_task_data):
        """測試成功建立日誌"""
        # 先建立一個任務
        task = task_repository.create(schemas.TaskCreate(**sample_task_data))

        log_create = schemas.LogCreate(
            task_id=task.id,
            level="INFO",
            message="測試訊息",
        )
        log = log_repository.create(log_create)

        assert log is not None
        assert log.id is not None
        assert log.task_id == task.id
        assert log.level == "INFO"
        assert log.message == "測試訊息"
        assert log.timestamp is not None

    def test_create_log_with_different_levels(
        self, log_repository, task_repository, sample_task_data
    ):
        """測試不同日誌等級"""
        task = task_repository.create(schemas.TaskCreate(**sample_task_data))

        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in levels:
            log_create = schemas.LogCreate(
                task_id=task.id,
                level=level,
                message=f"{level} 等級訊息",
            )
            log = log_repository.create(log_create)

            assert log.level == level


class TestLogRepositoryGetByTaskId:
    """測試 LogRepository.get_by_task_id 方法"""

    def test_get_by_task_id_success(
        self, log_repository, task_repository, sample_task_data
    ):
        """測試成功取得任務的日誌"""
        task = task_repository.create(schemas.TaskCreate(**sample_task_data))

        # 建立多筆日誌
        for i in range(3):
            log_create = schemas.LogCreate(
                task_id=task.id,
                level="INFO",
                message=f"日誌 {i}",
            )
            log_repository.create(log_create)

        logs = log_repository.get_by_task_id(task.id)

        assert len(logs) == 3

    def test_get_by_task_id_empty(self, log_repository, task_repository, sample_task_data):
        """測試取得沒有日誌的任務"""
        task = task_repository.create(schemas.TaskCreate(**sample_task_data))

        logs = log_repository.get_by_task_id(task.id)

        assert logs == []

    def test_get_by_task_id_not_found(self, log_repository):
        """測試取得不存在任務的日誌"""
        logs = log_repository.get_by_task_id("non-existent-task-id")
        assert logs == []

    def test_get_by_task_id_ordered_by_timestamp_desc(
        self, log_repository, task_repository, sample_task_data
    ):
        """測試日誌按時間戳降序排列"""
        task = task_repository.create(schemas.TaskCreate(**sample_task_data))

        # 建立多筆日誌
        log1 = log_repository.create(
            schemas.LogCreate(task_id=task.id, level="INFO", message="第一筆")
        )
        log2 = log_repository.create(
            schemas.LogCreate(task_id=task.id, level="INFO", message="第二筆")
        )
        log3 = log_repository.create(
            schemas.LogCreate(task_id=task.id, level="INFO", message="第三筆")
        )

        logs = log_repository.get_by_task_id(task.id)

        # 應該按時間戳降序排列 (最新的在前面)
        assert len(logs) == 3
        assert logs[0].id == log3.id
        assert logs[1].id == log2.id
        assert logs[2].id == log1.id

    def test_get_by_task_id_only_returns_task_logs(
        self, log_repository, task_repository, sample_task_data, sample_task_data_2
    ):
        """測試只回傳指定任務的日誌"""
        task1 = task_repository.create(schemas.TaskCreate(**sample_task_data))
        task2 = task_repository.create(schemas.TaskCreate(**sample_task_data_2))

        # 為兩個任務建立日誌
        log_repository.create(
            schemas.LogCreate(task_id=task1.id, level="INFO", message="任務1日誌")
        )
        log_repository.create(
            schemas.LogCreate(task_id=task2.id, level="INFO", message="任務2日誌")
        )

        logs_task1 = log_repository.get_by_task_id(task1.id)
        logs_task2 = log_repository.get_by_task_id(task2.id)

        assert len(logs_task1) == 1
        assert logs_task1[0].message == "任務1日誌"
        assert len(logs_task2) == 1
        assert logs_task2[0].message == "任務2日誌"
