import json

import pytest
from pathlib import Path

from backend.models.setting import Setting
from backend.utils.path_security import validate_path_within
from backend.worker.worker import process_completed_download, WorkerServices


class TestWebhookFilepathValidation:
    """Webhook worker filepath 路徑驗證測試"""

    def test_rejects_path_traversal_filepath(self, tmp_path, task_service, log_service):
        """含路徑穿越的 filepath 應被拒絕"""
        malicious_path = str(tmp_path / "downloads" / ".." / ".." / "etc" / "passwd")
        services = WorkerServices(task_service=task_service, log_service=log_service)
        # 不應拋出例外，但也不應處理檔案
        process_completed_download(malicious_path, services=services)

    def test_rejects_nonexistent_filepath(self, tmp_path, task_service, log_service):
        """不存在的 filepath 應被跳過"""
        fake_path = str(tmp_path / "nonexistent" / "file.mkv")
        services = WorkerServices(task_service=task_service, log_service=log_service)
        # 不應拋出例外
        process_completed_download(fake_path, services=services)

    def test_accepts_valid_filepath(self, tmp_path, task_service, log_service, db_session):
        """合法的 filepath 應正常處理"""
        # 建立測試檔案
        download_dir = tmp_path / "downloads"
        download_dir.mkdir()
        test_file = download_dir / "test_anime_ep01.mkv"
        test_file.write_bytes(b"fake video")

        services = WorkerServices(task_service=task_service, log_service=log_service)
        # 不應拋出例外（即使沒有匹配的任務）
        process_completed_download(str(test_file), services=services)


class TestTaskMoveTolValidation:
    """Task Service move_to 路徑白名單驗證測試"""

    def test_rejects_move_to_outside_allowed(
        self, task_service, setting_service, db_session, sample_task_data
    ):
        """move_to 不在白名單內應被拒絕"""
        # 設定 allowed_directories
        setting_service.set_allowed_directories(["/downloads"])

        sample_task_data["move_to"] = "/etc/cron.d/evil"
        from backend.schemas import TaskCreate
        task = TaskCreate(**sample_task_data)

        with pytest.raises(ValueError, match="不在允許的目錄"):
            task_service.create_task(task, allowed_directories=["/downloads"])

    def test_accepts_move_to_within_allowed(
        self, task_service, setting_service, db_session, sample_task_data
    ):
        """move_to 在白名單內應正常建立"""
        setting_service.set_allowed_directories(["/downloads"])

        sample_task_data["move_to"] = "/downloads/anime/show1"
        from backend.schemas import TaskCreate
        task = TaskCreate(**sample_task_data)

        result = task_service.create_task(task, allowed_directories=["/downloads"])
        assert result is not None

    def test_update_validates_move_to(
        self, task_service, setting_service, db_session, sample_task_data
    ):
        """更新任務時同樣驗證 move_to"""
        setting_service.set_allowed_directories(["/downloads"])

        sample_task_data["move_to"] = "/downloads/anime"
        from backend.schemas import TaskCreate, TaskUpdate
        task = TaskCreate(**sample_task_data)
        created = task_service.create_task(task, allowed_directories=["/downloads"])

        update_data = sample_task_data.copy()
        update_data["move_to"] = "/etc/evil"
        task_update = TaskUpdate(**update_data)

        with pytest.raises(ValueError, match="不在允許的目錄"):
            task_service.update_task(
                created.id, task_update, allowed_directories=["/downloads"]
            )
