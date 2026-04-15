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


class TestTaskRepositoryEpisodeOffset:
    """測試 TaskRepository 的 episode 偏移欄位"""

    def test_create_task_with_episode_offset(self, task_repository):
        """測試建立任務時包含偏移設定"""
        task_data = {
            "name": "偏移測試任務",
            "include": "關鍵字",
            "move_to": "/downloads/test",
            "rename_rule": "parse",
            "src_filename": "{title} - {episode}.mp4",
            "dst_filename": "{title} - S02E{episode}.mp4",
            "episode_offset_enabled": True,
            "episode_offset_group": "episode",
            "episode_offset_value": 12,
        }
        task_create = schemas.TaskCreate(**task_data)
        task = task_repository.create(task_create)

        assert task.episode_offset_enabled is True
        assert task.episode_offset_group == "episode"
        assert task.episode_offset_value == 12

    def test_create_task_default_episode_offset(self, task_repository):
        """測試建立任務時偏移欄位有正確預設值"""
        task_data = {
            "name": "預設偏移任務",
            "include": "關鍵字",
            "move_to": "/downloads/test",
        }
        task_create = schemas.TaskCreate(**task_data)
        task = task_repository.create(task_create)

        assert task.episode_offset_enabled is False
        assert task.episode_offset_group is None
        assert task.episode_offset_value == 0

    def test_update_task_episode_offset(self, task_repository, sample_task_data):
        """測試更新任務偏移設定"""
        task_create = schemas.TaskCreate(**sample_task_data)
        created_task = task_repository.create(task_create)

        update_data = schemas.TaskUpdate(
            name=sample_task_data["name"],
            include=sample_task_data["include"],
            move_to=sample_task_data["move_to"],
            episode_offset_enabled=True,
            episode_offset_group="episode",
            episode_offset_value=24,
        )
        updated_task = task_repository.update(created_task.id, update_data)

        assert updated_task.episode_offset_enabled is True
        assert updated_task.episode_offset_group == "episode"
        assert updated_task.episode_offset_value == 24

    def test_get_task_includes_episode_offset(self, task_repository):
        """測試取得任務時包含偏移欄位"""
        task_data = {
            "name": "偏移查詢任務",
            "include": "關鍵字",
            "move_to": "/downloads/test",
            "episode_offset_enabled": True,
            "episode_offset_group": "ep",
            "episode_offset_value": -5,
        }
        task_create = schemas.TaskCreate(**task_data)
        created_task = task_repository.create(task_create)

        found_task = task_repository.get_by_id(created_task.id)

        assert found_task.episode_offset_enabled is True
        assert found_task.episode_offset_group == "ep"
        assert found_task.episode_offset_value == -5


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


class TestTaskRepositoryBatchCreate:
    """測試 TaskRepository.batch_create 方法"""

    def test_batch_create_success(
        self, task_repository, sample_task_data, sample_task_data_2
    ):
        """成功批量建立多筆，DB 內可查得"""
        items = [
            schemas.TaskCreate(**sample_task_data),
            schemas.TaskCreate(**sample_task_data_2),
        ]

        created = task_repository.batch_create(items)

        assert len(created) == 2
        assert created[0].name == sample_task_data["name"]
        assert created[1].name == sample_task_data_2["name"]
        # 驗證 DB 實際可查得
        assert task_repository.get_by_name(sample_task_data["name"]) is not None
        assert task_repository.get_by_name(sample_task_data_2["name"]) is not None

    def test_batch_create_conflicts_with_existing_name(
        self, task_repository, sample_task_data, sample_task_data_2
    ):
        """批量中某筆 name 與 DB 現有重複，拋出 TaskAlreadyExists，整體未寫入"""
        from backend.exceptions.task_exception import TaskAlreadyExists

        # 先建立一筆
        task_repository.create(schemas.TaskCreate(**sample_task_data))

        # 批量建立：第 2 筆是新 name，第 1 筆與既有重名
        items = [
            schemas.TaskCreate(**sample_task_data),
            schemas.TaskCreate(**sample_task_data_2),
        ]

        with pytest.raises(TaskAlreadyExists):
            task_repository.batch_create(items)

        # 第 2 筆不應該被寫入（rollback）
        assert task_repository.get_by_name(sample_task_data_2["name"]) is None
        # 全部任務應仍然只有最初的 1 筆
        assert len(task_repository.get_all()) == 1

    def test_batch_create_intra_batch_duplicate(
        self, task_repository, sample_task_data
    ):
        """批量內部兩筆同名，拋出 TaskAlreadyExists，整體未寫入"""
        from backend.exceptions.task_exception import TaskAlreadyExists

        items = [
            schemas.TaskCreate(**sample_task_data),
            schemas.TaskCreate(**sample_task_data),
        ]

        with pytest.raises(TaskAlreadyExists):
            task_repository.batch_create(items)

        assert task_repository.get_all() == []


class TestTaskRepositoryBatchUpdate:
    """測試 TaskRepository.batch_update 方法"""

    def test_batch_update_enabled_success(
        self, task_repository, sample_task_data, sample_task_data_2
    ):
        """批量更新 enabled=False"""
        t1 = task_repository.create(schemas.TaskCreate(**sample_task_data))
        t2 = task_repository.create(schemas.TaskCreate(**sample_task_data_2))
        t3_data = {**sample_task_data, "name": "第三個任務"}
        t3 = task_repository.create(schemas.TaskCreate(**t3_data))

        items = [
            schemas.TaskBatchUpdateItem(id=t1.id, patch=schemas.TaskPatch(enabled=False)),
            schemas.TaskBatchUpdateItem(id=t2.id, patch=schemas.TaskPatch(enabled=False)),
            schemas.TaskBatchUpdateItem(id=t3.id, patch=schemas.TaskPatch(enabled=False)),
        ]

        updated = task_repository.batch_update(items)

        assert len(updated) == 3
        for u in updated:
            assert u.enabled is False

    def test_batch_update_missing_id_raises_not_found(
        self, task_repository, sample_task_data
    ):
        """其中一筆 id 不存在，拋出 TaskNotFound，整體未更新（rollback）"""
        from backend.exceptions.task_exception import TaskNotFound

        t1 = task_repository.create(schemas.TaskCreate(**sample_task_data))
        # 原本 enabled=True
        assert t1.enabled is True

        items = [
            schemas.TaskBatchUpdateItem(id=t1.id, patch=schemas.TaskPatch(enabled=False)),
            schemas.TaskBatchUpdateItem(
                id="non-existent-id", patch=schemas.TaskPatch(enabled=False)
            ),
        ]

        with pytest.raises(TaskNotFound):
            task_repository.batch_update(items)

        # t1 不應該被變更
        refreshed = task_repository.get_by_id(t1.id)
        assert refreshed is not None
        assert refreshed.enabled is True

    def test_batch_update_intra_batch_name_conflict(
        self, task_repository, sample_task_data, sample_task_data_2
    ):
        """兩筆 patch 欲改同名，拋出 TaskAlreadyExists"""
        from backend.exceptions.task_exception import TaskAlreadyExists

        t1 = task_repository.create(schemas.TaskCreate(**sample_task_data))
        t2 = task_repository.create(schemas.TaskCreate(**sample_task_data_2))

        items = [
            schemas.TaskBatchUpdateItem(id=t1.id, patch=schemas.TaskPatch(name="衝突名稱")),
            schemas.TaskBatchUpdateItem(id=t2.id, patch=schemas.TaskPatch(name="衝突名稱")),
        ]

        with pytest.raises(TaskAlreadyExists):
            task_repository.batch_update(items)

        # 雙方名稱皆未變
        assert task_repository.get_by_id(t1.id).name == sample_task_data["name"]
        assert task_repository.get_by_id(t2.id).name == sample_task_data_2["name"]

    def test_batch_update_partial_patch_preserves_other_fields(
        self, task_repository, sample_task_data
    ):
        """patch 僅含部分欄位時，其他欄位不變"""
        t1 = task_repository.create(schemas.TaskCreate(**sample_task_data))
        original_include = t1.include
        original_move_to = t1.move_to

        items = [
            schemas.TaskBatchUpdateItem(id=t1.id, patch=schemas.TaskPatch(enabled=False)),
        ]
        updated = task_repository.batch_update(items)

        assert updated[0].enabled is False
        assert updated[0].include == original_include
        assert updated[0].move_to == original_move_to


class TestTaskRepositoryBatchDelete:
    """測試 TaskRepository.batch_delete 方法"""

    def test_batch_delete_success(
        self, task_repository, sample_task_data, sample_task_data_2
    ):
        """批量刪除存在的多筆，DB 中被移除"""
        t1 = task_repository.create(schemas.TaskCreate(**sample_task_data))
        t2 = task_repository.create(schemas.TaskCreate(**sample_task_data_2))

        deleted = task_repository.batch_delete([t1.id, t2.id])

        assert set(deleted) == {t1.id, t2.id}
        assert task_repository.get_by_id(t1.id) is None
        assert task_repository.get_by_id(t2.id) is None

    def test_batch_delete_missing_id_raises_not_found(
        self, task_repository, sample_task_data
    ):
        """ids 含不存在 id，拋出 TaskNotFound，整體未刪除"""
        from backend.exceptions.task_exception import TaskNotFound

        t1 = task_repository.create(schemas.TaskCreate(**sample_task_data))

        with pytest.raises(TaskNotFound):
            task_repository.batch_delete([t1.id, "non-existent-id"])

        # t1 不應該被刪除
        assert task_repository.get_by_id(t1.id) is not None

    def test_batch_delete_empty_ids_raises(self, task_repository):
        """ids 為空，拋出 ValueError"""
        with pytest.raises(ValueError):
            task_repository.batch_delete([])


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
