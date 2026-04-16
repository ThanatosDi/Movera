"""
TaskService 單元測試
"""

import pytest

from backend import schemas
from backend.exceptions.task_exception import TaskAlreadyExists, TaskNotFound
from backend.services.task_service import TaskService


class TestTaskServiceGetAllTasks:
    """測試 TaskService.get_all_tasks 方法"""

    def test_get_all_tasks_empty(self, task_service):
        """測試空資料庫取得所有任務"""
        tasks = task_service.get_all_tasks()
        assert tasks == []

    def test_get_all_tasks_with_tasks(
        self, task_service, sample_task_data, sample_task_data_2
    ):
        """測試取得所有任務"""
        task_service.create_task(schemas.TaskCreate(**sample_task_data))
        task_service.create_task(schemas.TaskCreate(**sample_task_data_2))

        tasks = task_service.get_all_tasks()

        assert len(tasks) == 2


class TestTaskServiceGetEnabledTasks:
    """測試 TaskService.get_enabled_tasks 方法"""

    def test_get_enabled_tasks_empty(self, task_service):
        """測試空資料庫取得啟用任務"""
        tasks = task_service.get_enabled_tasks()
        assert tasks == []

    def test_get_enabled_tasks_mixed(
        self, task_service, sample_task_data, sample_task_data_2
    ):
        """測試取得啟用任務 (混合)"""
        task_service.create_task(schemas.TaskCreate(**sample_task_data))  # enabled=True
        task_service.create_task(schemas.TaskCreate(**sample_task_data_2))  # enabled=False

        enabled_tasks = task_service.get_enabled_tasks()

        assert len(enabled_tasks) == 1
        assert enabled_tasks[0].name == sample_task_data["name"]


class TestTaskServiceGetTaskById:
    """測試 TaskService.get_task_by_id 方法"""

    def test_get_task_by_id_success(self, task_service, sample_task_data):
        """測試成功取得任務"""
        created_task = task_service.create_task(schemas.TaskCreate(**sample_task_data))

        found_task = task_service.get_task_by_id(created_task.id)

        assert found_task is not None
        assert found_task.id == created_task.id

    def test_get_task_by_id_not_found(self, task_service):
        """測試取得不存在的任務"""
        found_task = task_service.get_task_by_id("non-existent-id")
        assert found_task is None


class TestTaskServiceGetTaskByName:
    """測試 TaskService.get_task_by_name 方法"""

    def test_get_task_by_name_success(self, task_service, sample_task_data):
        """測試成功用名稱取得任務"""
        task_service.create_task(schemas.TaskCreate(**sample_task_data))

        found_task = task_service.get_task_by_name(sample_task_data["name"])

        assert found_task is not None
        assert found_task.name == sample_task_data["name"]

    def test_get_task_by_name_not_found(self, task_service):
        """測試取得不存在名稱的任務"""
        found_task = task_service.get_task_by_name("不存在的任務")
        assert found_task is None


class TestTaskServiceCreateTask:
    """測試 TaskService.create_task 方法"""

    def test_create_task_success(self, task_service, sample_task_data):
        """測試成功建立任務"""
        task = task_service.create_task(schemas.TaskCreate(**sample_task_data))

        assert task is not None
        assert task.name == sample_task_data["name"]
        assert task.include == sample_task_data["include"]

    def test_create_task_duplicate_name(self, task_service, sample_task_data):
        """測試建立重複名稱的任務"""
        task_service.create_task(schemas.TaskCreate(**sample_task_data))

        with pytest.raises(TaskAlreadyExists) as exc_info:
            task_service.create_task(schemas.TaskCreate(**sample_task_data))

        assert sample_task_data["name"] in str(exc_info.value)


class TestTaskServiceUpdateTask:
    """測試 TaskService.update_task 方法"""

    def test_update_task_success(self, task_service, sample_task_data):
        """測試成功更新任務"""
        created_task = task_service.create_task(schemas.TaskCreate(**sample_task_data))

        update_data = schemas.TaskUpdate(
            name="更新後的名稱",
            include=sample_task_data["include"],
            move_to="/new/path",
        )
        updated_task = task_service.update_task(created_task.id, update_data)

        assert updated_task.name == "更新後的名稱"
        assert updated_task.move_to == "/new/path"

    def test_update_task_not_found(self, task_service, sample_task_data):
        """測試更新不存在的任務"""
        update_data = schemas.TaskUpdate(
            name="任何名稱",
            include="關鍵字",
            move_to="/path",
        )

        with pytest.raises(TaskNotFound) as exc_info:
            task_service.update_task("non-existent-id", update_data)

        assert "non-existent-id" in str(exc_info.value)

    def test_update_task_duplicate_name(
        self, task_service, sample_task_data, sample_task_data_2
    ):
        """測試更新為已存在的名稱"""
        task1 = task_service.create_task(schemas.TaskCreate(**sample_task_data))
        task2 = task_service.create_task(schemas.TaskCreate(**sample_task_data_2))

        # 嘗試將 task2 的名稱改為 task1 的名稱
        update_data = schemas.TaskUpdate(
            name=sample_task_data["name"],  # task1 的名稱
            include=sample_task_data_2["include"],
            move_to=sample_task_data_2["move_to"],
        )

        with pytest.raises(TaskAlreadyExists) as exc_info:
            task_service.update_task(task2.id, update_data)

        assert sample_task_data["name"] in str(exc_info.value)

    def test_update_task_same_name(self, task_service, sample_task_data):
        """測試更新時保持相同名稱 (應該成功)"""
        created_task = task_service.create_task(schemas.TaskCreate(**sample_task_data))

        # 名稱不變，只更新其他欄位
        update_data = schemas.TaskUpdate(
            name=sample_task_data["name"],
            include="新的關鍵字",
            move_to=sample_task_data["move_to"],
        )
        updated_task = task_service.update_task(created_task.id, update_data)

        assert updated_task.name == sample_task_data["name"]
        assert updated_task.include == "新的關鍵字"


class TestTaskServiceDeleteTask:
    """測試 TaskService.delete_task 方法"""

    def test_delete_task_success(self, task_service, sample_task_data):
        """測試成功刪除任務"""
        created_task = task_service.create_task(schemas.TaskCreate(**sample_task_data))

        deleted_task = task_service.delete_task(created_task.id)

        assert deleted_task.id == created_task.id
        # 確認已刪除
        assert task_service.get_task_by_id(created_task.id) is None

    def test_delete_task_not_found(self, task_service):
        """測試刪除不存在的任務"""
        with pytest.raises(TaskNotFound) as exc_info:
            task_service.delete_task("non-existent-id")

        assert "non-existent-id" in str(exc_info.value)


class TestTaskServiceBatch:
    """測試 TaskService 的批量方法"""

    def test_batch_create_tasks_success(
        self, task_service, sample_task_data, sample_task_data_2
    ):
        """批量建立委派至 repository 並回傳結果"""
        items = [
            schemas.TaskCreate(**sample_task_data),
            schemas.TaskCreate(**sample_task_data_2),
        ]
        created = task_service.batch_create_tasks(items)

        assert len(created) == 2
        assert created[0].name == sample_task_data["name"]

    def test_batch_create_propagates_duplicate_error(
        self, task_service, sample_task_data
    ):
        """批量建立重名時例外往上拋"""
        task_service.create_task(schemas.TaskCreate(**sample_task_data))

        items = [schemas.TaskCreate(**sample_task_data)]
        with pytest.raises(TaskAlreadyExists):
            task_service.batch_create_tasks(items)

    def test_batch_update_tasks_success(
        self, task_service, sample_task_data, sample_task_data_2
    ):
        """批量更新 enabled=False"""
        t1 = task_service.create_task(schemas.TaskCreate(**sample_task_data))
        t2 = task_service.create_task(schemas.TaskCreate(**sample_task_data_2))

        items = [
            schemas.TaskBatchUpdateItem(
                id=t1.id, patch=schemas.TaskPatch(enabled=False)
            ),
            schemas.TaskBatchUpdateItem(
                id=t2.id, patch=schemas.TaskPatch(enabled=True)
            ),
        ]
        updated = task_service.batch_update_tasks(items)

        assert len(updated) == 2
        assert updated[0].enabled is False
        assert updated[1].enabled is True

    def test_batch_update_name_conflict_propagates(
        self, task_service, sample_task_data, sample_task_data_2
    ):
        """批量更新時 patch name 與其他既有任務衝突，例外往上拋"""
        t1 = task_service.create_task(schemas.TaskCreate(**sample_task_data))
        task_service.create_task(schemas.TaskCreate(**sample_task_data_2))

        # 將 t1 的 name 改為 t2 的 name
        items = [
            schemas.TaskBatchUpdateItem(
                id=t1.id,
                patch=schemas.TaskPatch(name=sample_task_data_2["name"]),
            ),
        ]
        with pytest.raises(TaskAlreadyExists):
            task_service.batch_update_tasks(items)

    def test_batch_update_not_found_propagates(self, task_service):
        """批量更新 id 不存在，TaskNotFound 往上拋"""
        items = [
            schemas.TaskBatchUpdateItem(
                id="non-existent", patch=schemas.TaskPatch(enabled=False)
            ),
        ]
        with pytest.raises(TaskNotFound):
            task_service.batch_update_tasks(items)

    def test_batch_delete_tasks_success(
        self, task_service, sample_task_data, sample_task_data_2
    ):
        """批量刪除委派至 repository"""
        t1 = task_service.create_task(schemas.TaskCreate(**sample_task_data))
        t2 = task_service.create_task(schemas.TaskCreate(**sample_task_data_2))

        deleted = task_service.batch_delete_tasks([t1.id, t2.id])

        assert set(deleted) == {t1.id, t2.id}
        assert task_service.get_task_by_id(t1.id) is None
        assert task_service.get_task_by_id(t2.id) is None

    def test_batch_delete_not_found_propagates(self, task_service, sample_task_data):
        """批量刪除 id 不存在，TaskNotFound 往上拋"""
        t1 = task_service.create_task(schemas.TaskCreate(**sample_task_data))

        with pytest.raises(TaskNotFound):
            task_service.batch_delete_tasks([t1.id, "non-existent"])

        # t1 仍存在
        assert task_service.get_task_by_id(t1.id) is not None
