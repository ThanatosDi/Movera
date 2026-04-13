"""
Worker 單元測試
"""

import pytest
from unittest.mock import patch, MagicMock

from backend.exceptions.worker_exception import MoveOperationError, RenameOperationError
from backend.worker.worker import (
    WorkerServices,
    create_worker_services,
    is_path_within_allowed,
    web_logger,
    match_task,
    perform_rename_operation,
    perform_move_operation,
    process_completed_download,
)


@pytest.fixture
def mock_services():
    """建立 mock 的 WorkerServices"""
    task_service = MagicMock()
    log_service = MagicMock()
    setting_service = MagicMock()
    setting_service.get_allowed_source_directories.return_value = []
    return WorkerServices(
        task_service=task_service,
        log_service=log_service,
        setting_service=setting_service,
    )


class TestWorkerServices:
    """測試 Worker 服務管理"""

    def test_create_worker_services(self):
        """測試工廠函式建立服務"""
        with patch("backend.worker.worker.SessionLocal") as mock_session:
            with patch("backend.worker.worker.TaskRepository"):
                with patch("backend.worker.worker.LogRepository"):
                    with patch("backend.worker.worker.SettingRepository"):
                        with patch("backend.worker.worker.TaskService"):
                            with patch("backend.worker.worker.LogService"):
                                with patch("backend.worker.worker.SettingService"):
                                    services = create_worker_services()
                                    assert services.task_service is not None
                                    assert services.log_service is not None
                                    assert services.setting_service is not None

    def test_no_global_state(self):
        """確認模組中不存在 global 變數宣告"""
        import inspect
        import backend.worker.worker as worker_module

        source = inspect.getsource(worker_module)
        assert "global " not in source, "模組中不應存在 global 變數宣告"


class TestWebLogger:
    """測試 web_logger 函數"""

    def test_web_logger_info(self, mock_services):
        """測試 INFO 等級的日誌"""
        web_logger(
            services=mock_services,
            task_id="test-task-id",
            level="INFO",
            message="測試訊息",
        )

        mock_services.log_service.create_log.assert_called_once()
        call_args = mock_services.log_service.create_log.call_args[0][0]
        assert call_args.task_id == "test-task-id"
        assert call_args.level == "INFO"
        assert call_args.message == "測試訊息"

    def test_web_logger_error(self, mock_services):
        """測試 ERROR 等級的日誌"""
        web_logger(
            services=mock_services,
            task_id="test-task-id",
            level="ERROR",
            message="錯誤訊息",
        )

        call_args = mock_services.log_service.create_log.call_args[0][0]
        assert call_args.level == "ERROR"

    def test_web_logger_level_uppercase(self, mock_services):
        """測試等級會轉為大寫"""
        web_logger(
            services=mock_services,
            task_id="test-task-id",
            level="info",
            message="測試訊息",
        )

        call_args = mock_services.log_service.create_log.call_args[0][0]
        assert call_args.level == "INFO"


class TestMatchTask:
    """測試 match_task 函數"""

    def test_match_task_success(self, mock_services):
        """測試成功匹配任務"""
        task1 = MagicMock()
        task1.id = "task-1"
        task1.name = "動畫任務"
        task1.include = "動畫名稱"

        task2 = MagicMock()
        task2.id = "task-2"
        task2.name = "電影任務"
        task2.include = "電影名稱"

        tasks = [task1, task2]
        filepath = "/downloads/動畫名稱 - 01.mp4"

        result = match_task(mock_services, tasks, filepath)

        assert result == task1
        mock_services.log_service.create_log.assert_called_once()

    def test_match_task_no_match(self, mock_services):
        """測試無匹配的情況"""
        task1 = MagicMock()
        task1.include = "動畫名稱"

        tasks = [task1]
        filepath = "/downloads/不相關的檔案.mp4"

        result = match_task(mock_services, tasks, filepath)

        assert result is None
        mock_services.log_service.create_log.assert_not_called()

    def test_match_task_first_match(self, mock_services):
        """測試回傳第一個匹配的任務"""
        task1 = MagicMock()
        task1.id = "task-1"
        task1.name = "任務1"
        task1.include = "關鍵字"

        task2 = MagicMock()
        task2.id = "task-2"
        task2.name = "任務2"
        task2.include = "關鍵字"

        tasks = [task1, task2]
        filepath = "/downloads/關鍵字檔案.mp4"

        result = match_task(mock_services, tasks, filepath)

        assert result == task1


class TestPerformRenameOperation:
    """測試 perform_rename_operation 函數"""

    @patch("backend.worker.worker.Rename")
    def test_perform_rename_no_rule(self, mock_rename, mock_services):
        """測試沒有重命名規則時"""
        task = MagicMock()
        task.rename_rule = None
        filepath = "/downloads/test.mp4"

        result = perform_rename_operation(mock_services, task, filepath)

        assert result == filepath
        mock_rename.assert_not_called()

    @patch("backend.worker.worker.Rename")
    def test_perform_rename_success(self, mock_rename, mock_services):
        """測試成功重命名"""
        task = MagicMock()
        task.id = "test-task-id"
        task.rename_rule = "regex"
        task.src_filename = r"(.+) - (\d+).mp4"
        task.dst_filename = r"\1 - S01E\2.mp4"

        mock_rename_instance = MagicMock()
        mock_rename_instance.execute_rename.return_value = "/downloads/動畫 - S01E01.mp4"
        mock_rename.return_value = mock_rename_instance

        filepath = "/downloads/動畫 - 01.mp4"

        result = perform_rename_operation(mock_services, task, filepath)

        assert result == "/downloads/動畫 - S01E01.mp4"
        mock_services.log_service.create_log.assert_called_once()

    @patch("backend.worker.worker.Rename")
    def test_perform_rename_error(self, mock_rename, mock_services):
        """測試重命名失敗時拋出異常"""
        task = MagicMock()
        task.id = "test-task-id"
        task.rename_rule = "regex"
        task.src_filename = r"(.+)"
        task.dst_filename = r"\1"

        mock_rename_instance = MagicMock()
        mock_rename_instance.execute_rename.side_effect = ValueError("重命名失敗")
        mock_rename.return_value = mock_rename_instance

        filepath = "/downloads/test.mp4"

        with pytest.raises(RenameOperationError) as exc_info:
            perform_rename_operation(mock_services, task, filepath)

        assert exc_info.value.filepath == filepath
        assert "重命名失敗" in exc_info.value.reason

        # 應該記錄錯誤日誌
        assert mock_services.log_service.create_log.call_count == 1


class TestPerformMoveOperation:
    """測試 perform_move_operation 函數"""

    @patch("backend.worker.worker.move")
    def test_perform_move_success(self, mock_move, mock_services):
        """測試成功移動檔案"""
        task = MagicMock()
        task.id = "test-task-id"
        task.move_to = "/target/folder"
        filepath = "/downloads/test.mp4"

        perform_move_operation(mock_services, task, filepath)

        mock_move.assert_called_once_with(filepath, "/target/folder")
        mock_services.log_service.create_log.assert_called_once()

    @patch("backend.worker.worker.move")
    def test_perform_move_error(self, mock_move, mock_services):
        """測試移動檔案失敗時拋出異常"""
        task = MagicMock()
        task.id = "test-task-id"
        task.move_to = "/target/folder"

        mock_move.side_effect = OSError("移動失敗")
        filepath = "/downloads/test.mp4"

        with pytest.raises(MoveOperationError) as exc_info:
            perform_move_operation(mock_services, task, filepath)

        assert exc_info.value.filepath == filepath
        assert exc_info.value.destination == "/target/folder"
        assert "移動失敗" in exc_info.value.reason


class TestIsPathWithinAllowed:
    """測試 is_path_within_allowed 函數"""

    def test_path_within_allowed(self):
        """測試路徑在允許範圍內"""
        assert is_path_within_allowed("/downloads/anime/test.mp4", ["/downloads"]) is True

    def test_path_not_within_allowed(self):
        """測試路徑不在允許範圍內"""
        assert is_path_within_allowed("/etc/passwd", ["/downloads"]) is False

    def test_path_with_multiple_allowed(self):
        """測試多個允許目錄"""
        assert is_path_within_allowed("/media/movie.mp4", ["/downloads", "/media"]) is True

    def test_empty_allowed_list(self):
        """測試空白名單"""
        assert is_path_within_allowed("/downloads/test.mp4", []) is False


class TestProcessCompletedDownload:
    """測試 process_completed_download 函數"""

    @patch("backend.worker.worker.perform_move_operation")
    @patch("backend.worker.worker.perform_rename_operation")
    @patch("backend.worker.worker.match_task")
    def test_process_completed_download_blocked_by_source_whitelist(
        self, mock_match_task, mock_rename, mock_move, mock_services,
    ):
        """測試來源路徑不在白名單內時拒絕處理"""
        mock_services.setting_service.get_allowed_source_directories.return_value = ["/downloads"]

        result = process_completed_download("/etc/passwd", services=mock_services)

        assert result is None
        mock_services.task_service.get_enabled_tasks.assert_not_called()
        mock_match_task.assert_not_called()
        mock_rename.assert_not_called()
        mock_move.assert_not_called()

    @patch("backend.worker.worker.perform_move_operation")
    @patch("backend.worker.worker.perform_rename_operation")
    @patch("backend.worker.worker.match_task")
    def test_process_completed_download_allowed_by_source_whitelist(
        self, mock_match_task, mock_rename, mock_move, mock_services,
    ):
        """測試來源路徑在白名單內時正常處理"""
        mock_services.setting_service.get_allowed_source_directories.return_value = ["/downloads"]
        mock_services.task_service.get_enabled_tasks.return_value = []
        mock_match_task.return_value = None

        process_completed_download("/downloads/test.mp4", services=mock_services)

        mock_services.task_service.get_enabled_tasks.assert_called_once()

    @patch("backend.worker.worker.perform_move_operation")
    @patch("backend.worker.worker.perform_rename_operation")
    @patch("backend.worker.worker.match_task")
    def test_process_completed_download_empty_whitelist_allows_all(
        self, mock_match_task, mock_rename, mock_move, mock_services,
    ):
        """測試白名單為空時允許所有路徑（向後相容）"""
        mock_services.setting_service.get_allowed_source_directories.return_value = []
        mock_services.task_service.get_enabled_tasks.return_value = []
        mock_match_task.return_value = None

        process_completed_download("/any/path/test.mp4", services=mock_services)

        mock_services.task_service.get_enabled_tasks.assert_called_once()

    @patch("backend.worker.worker.perform_move_operation")
    @patch("backend.worker.worker.perform_rename_operation")
    @patch("backend.worker.worker.match_task")
    def test_process_completed_download_no_match(
        self, mock_match_task, mock_rename, mock_move, mock_services,
    ):
        """測試沒有匹配的任務"""
        mock_services.task_service.get_enabled_tasks.return_value = []
        mock_match_task.return_value = None

        result = process_completed_download("/downloads/test.mp4", services=mock_services)

        assert result is None
        mock_rename.assert_not_called()
        mock_move.assert_not_called()

    @patch("backend.worker.worker.perform_move_operation")
    @patch("backend.worker.worker.perform_rename_operation")
    @patch("backend.worker.worker.match_task")
    def test_process_completed_download_success(
        self, mock_match_task, mock_rename, mock_move, mock_services,
    ):
        """測試成功處理下載完成"""
        mock_task = MagicMock()
        mock_task.include = "關鍵字"
        mock_task.move_to = "/target"

        mock_services.task_service.get_enabled_tasks.return_value = [mock_task]
        mock_match_task.return_value = mock_task
        mock_rename.return_value = "/downloads/renamed.mp4"

        process_completed_download("/downloads/關鍵字檔案.mp4", services=mock_services)

        mock_rename.assert_called_once_with(mock_services, mock_task, "/downloads/關鍵字檔案.mp4")
        mock_move.assert_called_once_with(mock_services, mock_task, "/downloads/renamed.mp4")

    @patch("backend.worker.worker.perform_move_operation")
    @patch("backend.worker.worker.perform_rename_operation")
    @patch("backend.worker.worker.match_task")
    def test_process_completed_download_skip_rename(
        self, mock_match_task, mock_rename, mock_move, mock_services,
    ):
        """測試跳過重命名 (當 rename_rule 為 None)"""
        mock_task = MagicMock()
        mock_task.include = "關鍵字"
        mock_task.rename_rule = None

        mock_services.task_service.get_enabled_tasks.return_value = [mock_task]
        mock_match_task.return_value = mock_task
        mock_rename.return_value = "/downloads/關鍵字檔案.mp4"

        process_completed_download("/downloads/關鍵字檔案.mp4", services=mock_services)

        mock_move.assert_called_once()

    @patch("backend.worker.worker.perform_move_operation")
    @patch("backend.worker.worker.perform_rename_operation")
    @patch("backend.worker.worker.match_task")
    def test_process_completed_download_rename_error(
        self, mock_match_task, mock_rename, mock_move, mock_services,
    ):
        """測試重命名失敗時不執行移動"""
        mock_task = MagicMock()
        mock_task.include = "關鍵字"

        mock_services.task_service.get_enabled_tasks.return_value = [mock_task]
        mock_match_task.return_value = mock_task
        mock_rename.side_effect = RenameOperationError("/downloads/test.mp4", "錯誤")

        process_completed_download("/downloads/關鍵字檔案.mp4", services=mock_services)

        mock_move.assert_not_called()

    @patch("backend.worker.worker.perform_move_operation")
    @patch("backend.worker.worker.perform_rename_operation")
    @patch("backend.worker.worker.match_task")
    def test_process_completed_download_move_error(
        self, mock_match_task, mock_rename, mock_move, mock_services,
    ):
        """測試移動失敗時正常處理"""
        mock_task = MagicMock()
        mock_task.include = "關鍵字"
        mock_task.move_to = "/target"

        mock_services.task_service.get_enabled_tasks.return_value = [mock_task]
        mock_match_task.return_value = mock_task
        mock_rename.return_value = "/downloads/renamed.mp4"
        mock_move.side_effect = MoveOperationError(
            "/downloads/renamed.mp4", "/target", "錯誤"
        )

        process_completed_download("/downloads/關鍵字檔案.mp4", services=mock_services)

        mock_rename.assert_called_once()
        mock_move.assert_called_once()
