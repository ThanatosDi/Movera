"""
TaskRepository 單元測試
"""

import pytest

from backend import schemas
from backend.repositories.task import TaskRepository


class TestTaskRepositoryCreate:
    """測試 TaskRepository.create 方法"""

    def test_create_task_success(self, task_repository, sample_task_data):
        """測試成功建立任務"""
        task_create = schemas.TaskCreate(**sample_task_data)
        task = task_repository.create(task_create)

        assert task is not None
        assert task.id is not None
        assert task.name == sample_task_data["name"]
        assert task.include == sample_task_data["include"]
        assert task.move_to == sample_task_data["move_to"]
        assert task.enabled == sample_task_data["enabled"]

    def test_create_task_with_minimal_data(self, task_repository):
        """測試使用最少必要資料建立任務"""
        minimal_data = {
            "name": "最小任務",
            "include": "關鍵字",
            "move_to": "/path/to/dir",
        }
        task_create = schemas.TaskCreate(**minimal_data)
        task = task_repository.create(task_create)

        assert task is not None
        assert task.name == "最小任務"
        assert task.enabled is True  # 預設值
        assert task.rename_rule is None


class TestTaskRepositoryGetById:
    """測試 TaskRepository.get_by_id 方法"""

    def test_get_by_id_success(self, task_repository, sample_task_data):
        """測試成功取得任務"""
        task_create = schemas.TaskCreate(**sample_task_data)
        created_task = task_repository.create(task_create)

        found_task = task_repository.get_by_id(created_task.id)

        assert found_task is not None
        assert found_task.id == created_task.id
        assert found_task.name == sample_task_data["name"]

    def test_get_by_id_not_found(self, task_repository):
        """測試取得不存在的任務"""
        found_task = task_repository.get_by_id("non-existent-id")
        assert found_task is None


class TestTaskRepositoryGetByName:
    """測試 TaskRepository.get_by_name 方法"""

    def test_get_by_name_success(self, task_repository, sample_task_data):
        """測試成功用名稱取得任務"""
        task_create = schemas.TaskCreate(**sample_task_data)
        task_repository.create(task_create)

        found_task = task_repository.get_by_name(sample_task_data["name"])

        assert found_task is not None
        assert found_task.name == sample_task_data["name"]

    def test_get_by_name_not_found(self, task_repository):
        """測試取得不存在名稱的任務"""
        found_task = task_repository.get_by_name("不存在的任務")
        assert found_task is None


class TestTaskRepositoryGetAll:
    """測試 TaskRepository.get_all 方法"""

    def test_get_all_empty(self, task_repository):
        """測試空資料庫取得所有任務"""
        tasks = task_repository.get_all()
        assert tasks == []

    def test_get_all_with_tasks(
        self, task_repository, sample_task_data, sample_task_data_2
    ):
        """測試取得所有任務"""
        task_repository.create(schemas.TaskCreate(**sample_task_data))
        task_repository.create(schemas.TaskCreate(**sample_task_data_2))

        tasks = task_repository.get_all()

        assert len(tasks) == 2


class TestTaskRepositoryUpdate:
    """測試 TaskRepository.update 方法"""

    def test_update_task_success(self, task_repository, sample_task_data):
        """測試成功更新任務"""
        task_create = schemas.TaskCreate(**sample_task_data)
        created_task = task_repository.create(task_create)

        update_data = schemas.TaskUpdate(
            name="更新後的名稱",
            include=sample_task_data["include"],
            move_to="/new/path",
        )
        updated_task = task_repository.update(created_task.id, update_data)

        assert updated_task is not None
        assert updated_task.name == "更新後的名稱"
        assert updated_task.move_to == "/new/path"

    def test_update_task_not_found(self, task_repository, sample_task_data):
        """測試更新不存在的任務"""
        update_data = schemas.TaskUpdate(
            name="任何名稱",
            include="關鍵字",
            move_to="/path",
        )
        updated_task = task_repository.update("non-existent-id", update_data)

        assert updated_task is None

    def test_update_task_partial(self, task_repository, sample_task_data):
        """測試部分更新任務"""
        task_create = schemas.TaskCreate(**sample_task_data)
        created_task = task_repository.create(task_create)

        update_data = schemas.TaskUpdate(
            name=sample_task_data["name"],
            include=sample_task_data["include"],
            move_to=sample_task_data["move_to"],
            enabled=False,
        )
        updated_task = task_repository.update(created_task.id, update_data)

        assert updated_task is not None
        assert updated_task.enabled is False
        # 其他欄位保持不變
        assert updated_task.include == sample_task_data["include"]


class TestTaskRepositoryDelete:
    """測試 TaskRepository.delete 方法"""

    def test_delete_task_success(self, task_repository, sample_task_data):
        """測試成功刪除任務"""
        task_create = schemas.TaskCreate(**sample_task_data)
        created_task = task_repository.create(task_create)

        deleted_task = task_repository.delete(created_task.id)

        assert deleted_task is not None
        assert deleted_task.id == created_task.id
        # 確認已刪除
        assert task_repository.get_by_id(created_task.id) is None

    def test_delete_task_not_found(self, task_repository):
        """測試刪除不存在的任務"""
        deleted_task = task_repository.delete("non-existent-id")
        assert deleted_task is None


class TestTaskRepositoryGetStats:
    """測試 TaskRepository.get_stats 方法"""

    def test_get_stats_empty(self, task_repository):
        """測試空資料庫的統計"""
        stats = task_repository.get_stats()

        assert stats.enabled == 0
        assert stats.disabled == 0

    def test_get_stats_with_tasks(
        self, task_repository, sample_task_data, sample_task_data_2
    ):
        """測試有任務時的統計"""
        # sample_task_data: enabled=True
        # sample_task_data_2: enabled=False
        task_repository.create(schemas.TaskCreate(**sample_task_data))
        task_repository.create(schemas.TaskCreate(**sample_task_data_2))

        stats = task_repository.get_stats()

        assert stats.enabled == 1
        assert stats.disabled == 1


class TestTaskRepositoryGetEnabledTasks:
    """測試 TaskRepository.get_enabled_tasks 方法"""

    def test_get_enabled_tasks_empty(self, task_repository):
        """測試空資料庫取得啟用任務"""
        tasks = task_repository.get_enabled_tasks()
        assert tasks == []

    def test_get_enabled_tasks_with_mixed(
        self, task_repository, sample_task_data, sample_task_data_2
    ):
        """測試取得啟用的任務 (混合啟用/停用)"""
        task_repository.create(schemas.TaskCreate(**sample_task_data))  # enabled=True
        task_repository.create(schemas.TaskCreate(**sample_task_data_2))  # enabled=False

        enabled_tasks = task_repository.get_enabled_tasks()

        assert len(enabled_tasks) == 1
        assert enabled_tasks[0].name == sample_task_data["name"]
