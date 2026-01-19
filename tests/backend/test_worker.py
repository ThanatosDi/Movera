"""
Worker 單元測試
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from backend import schemas


class TestWebLogger:
    """測試 web_logger 函數"""

    @patch("backend.worker.worker.log_service")
    def test_web_logger_info(self, mock_log_service):
        """測試 INFO 等級的日誌"""
        from backend.worker.worker import web_logger

        web_logger(
            task_id="test-task-id",
            level="INFO",
            message="測試訊息",
        )

        mock_log_service.create_log.assert_called_once()
        call_args = mock_log_service.create_log.call_args[0][0]
        assert call_args.task_id == "test-task-id"
        assert call_args.level == "INFO"
        assert call_args.message == "測試訊息"

    @patch("backend.worker.worker.log_service")
    def test_web_logger_error(self, mock_log_service):
        """測試 ERROR 等級的日誌"""
        from backend.worker.worker import web_logger

        web_logger(
            task_id="test-task-id",
            level="ERROR",
            message="錯誤訊息",
        )

        call_args = mock_log_service.create_log.call_args[0][0]
        assert call_args.level == "ERROR"

    @patch("backend.worker.worker.log_service")
    def test_web_logger_level_uppercase(self, mock_log_service):
        """測試等級會轉為大寫"""
        from backend.worker.worker import web_logger

        web_logger(
            task_id="test-task-id",
            level="info",  # 小寫
            message="測試訊息",
        )

        call_args = mock_log_service.create_log.call_args[0][0]
        assert call_args.level == "INFO"


class TestMatchTask:
    """測試 match_task 函數"""

    @patch("backend.worker.worker.web_logger")
    def test_match_task_success(self, mock_logger):
        """測試成功匹配任務"""
        from backend.worker.worker import match_task

        # 建立 mock 任務
        task1 = MagicMock()
        task1.id = "task-1"
        task1.name = "動畫任務"
        task1.include = "動畫名稱"

        task2 = MagicMock()
        task2.id = "task-2"
        task2.name = "電影任務"
        task2.include = "電影名稱"

        tasks = [task1, task2]
        task_includes = [t.include for t in tasks]
        filepath = "/downloads/動畫名稱 - 01.mp4"

        result = match_task(tasks, task_includes, filepath)

        assert result == task1
        mock_logger.assert_called_once()

    @patch("backend.worker.worker.web_logger")
    def test_match_task_no_match(self, mock_logger):
        """測試無匹配的情況"""
        from backend.worker.worker import match_task

        task1 = MagicMock()
        task1.include = "動畫名稱"

        tasks = [task1]
        task_includes = [t.include for t in tasks]
        filepath = "/downloads/不相關的檔案.mp4"

        result = match_task(tasks, task_includes, filepath)

        assert result is None
        mock_logger.assert_not_called()

    @patch("backend.worker.worker.web_logger")
    def test_match_task_first_match(self, mock_logger):
        """測試回傳第一個匹配的任務"""
        from backend.worker.worker import match_task

        task1 = MagicMock()
        task1.id = "task-1"
        task1.name = "任務1"
        task1.include = "關鍵字"

        task2 = MagicMock()
        task2.id = "task-2"
        task2.name = "任務2"
        task2.include = "關鍵字"  # 相同關鍵字

        tasks = [task1, task2]
        task_includes = [t.include for t in tasks]
        filepath = "/downloads/關鍵字檔案.mp4"

        result = match_task(tasks, task_includes, filepath)

        # 應該回傳第一個匹配的
        assert result == task1


class TestPerformRenameOperation:
    """測試 perform_rename_operation 函數"""

    @patch("backend.worker.worker.web_logger")
    @patch("backend.worker.worker.Rename")
    def test_perform_rename_no_rule(self, mock_rename, mock_logger):
        """測試沒有重命名規則時"""
        from backend.worker.worker import perform_rename_operation

        task = MagicMock()
        task.rename_rule = None
        filepath = "/downloads/test.mp4"

        result = perform_rename_operation(task, filepath)

        assert result == filepath
        mock_rename.assert_not_called()

    @patch("backend.worker.worker.web_logger")
    @patch("backend.worker.worker.Rename")
    def test_perform_rename_success(self, mock_rename, mock_logger):
        """測試成功重命名"""
        from backend.worker.worker import perform_rename_operation

        task = MagicMock()
        task.id = "test-task-id"
        task.rename_rule = "regex"
        task.src_filename = r"(.+) - (\d+).mp4"
        task.dst_filename = r"\1 - S01E\2.mp4"

        mock_rename_instance = MagicMock()
        mock_rename_instance.execute_rename.return_value = "/downloads/動畫 - S01E01.mp4"
        mock_rename.return_value = mock_rename_instance

        filepath = "/downloads/動畫 - 01.mp4"

        result = perform_rename_operation(task, filepath)

        assert result == "/downloads/動畫 - S01E01.mp4"
        mock_logger.assert_called_once()

    @patch("backend.worker.worker.web_logger")
    @patch("backend.worker.worker.Rename")
    def test_perform_rename_error(self, mock_rename, mock_logger):
        """測試重命名失敗"""
        from backend.worker.worker import perform_rename_operation

        task = MagicMock()
        task.id = "test-task-id"
        task.rename_rule = "regex"
        task.src_filename = r"(.+)"
        task.dst_filename = r"\1"

        mock_rename_instance = MagicMock()
        mock_rename_instance.execute_rename.side_effect = Exception("重命名失敗")
        mock_rename.return_value = mock_rename_instance

        filepath = "/downloads/test.mp4"

        result = perform_rename_operation(task, filepath)

        # 發生錯誤時不會回傳值
        assert result is None
        # 應該記錄錯誤日誌
        mock_logger.assert_called()
        call_args = mock_logger.call_args
        assert call_args[1]["level"] == "ERROR"


class TestPerformMoveOperation:
    """測試 perform_move_operation 函數"""

    @patch("backend.worker.worker.web_logger")
    @patch("backend.worker.worker.move")
    def test_perform_move_success(self, mock_move, mock_logger):
        """測試成功移動檔案"""
        from backend.worker.worker import perform_move_operation

        task = MagicMock()
        task.id = "test-task-id"
        task.move_to = "/target/folder"
        filepath = "/downloads/test.mp4"

        perform_move_operation(task, filepath)

        mock_move.assert_called_once_with(filepath, "/target/folder")
        mock_logger.assert_called_once()
        call_args = mock_logger.call_args
        assert call_args[1]["level"] == "INFO"

    @patch("backend.worker.worker.web_logger")
    @patch("backend.worker.worker.move")
    def test_perform_move_error(self, mock_move, mock_logger):
        """測試移動檔案失敗"""
        from backend.worker.worker import perform_move_operation

        task = MagicMock()
        task.id = "test-task-id"
        task.move_to = "/target/folder"

        mock_move.side_effect = Exception("移動失敗")
        filepath = "/downloads/test.mp4"

        perform_move_operation(task, filepath)

        # 應該記錄錯誤日誌
        mock_logger.assert_called()
        call_args = mock_logger.call_args
        assert call_args[1]["level"] == "ERROR"


class TestProcessCompletedDownload:
    """測試 process_completed_download 函數"""

    @patch("backend.worker.worker.perform_move_operation")
    @patch("backend.worker.worker.perform_rename_operation")
    @patch("backend.worker.worker.match_task")
    @patch("backend.worker.worker.task_service")
    def test_process_completed_download_no_match(
        self,
        mock_task_service,
        mock_match_task,
        mock_rename,
        mock_move,
    ):
        """測試沒有匹配的任務"""
        from backend.worker.worker import process_completed_download

        mock_task_service.get_enabled_tasks.return_value = []
        mock_match_task.return_value = None

        result = process_completed_download("/downloads/test.mp4")

        assert result is None
        mock_rename.assert_not_called()
        mock_move.assert_not_called()

    @patch("backend.worker.worker.perform_move_operation")
    @patch("backend.worker.worker.perform_rename_operation")
    @patch("backend.worker.worker.match_task")
    @patch("backend.worker.worker.task_service")
    def test_process_completed_download_success(
        self,
        mock_task_service,
        mock_match_task,
        mock_rename,
        mock_move,
    ):
        """測試成功處理下載完成"""
        from backend.worker.worker import process_completed_download

        mock_task = MagicMock()
        mock_task.include = "關鍵字"
        mock_task.move_to = "/target"

        mock_task_service.get_enabled_tasks.return_value = [mock_task]
        mock_match_task.return_value = mock_task
        mock_rename.return_value = "/downloads/renamed.mp4"

        process_completed_download("/downloads/關鍵字檔案.mp4")

        mock_rename.assert_called_once_with(mock_task, "/downloads/關鍵字檔案.mp4")
        mock_move.assert_called_once_with(mock_task, "/downloads/renamed.mp4")

    @patch("backend.worker.worker.perform_move_operation")
    @patch("backend.worker.worker.perform_rename_operation")
    @patch("backend.worker.worker.match_task")
    @patch("backend.worker.worker.task_service")
    def test_process_completed_download_skip_rename(
        self,
        mock_task_service,
        mock_match_task,
        mock_rename,
        mock_move,
    ):
        """測試跳過重命名 (當 rename_rule 為 None)"""
        from backend.worker.worker import process_completed_download

        mock_task = MagicMock()
        mock_task.include = "關鍵字"
        mock_task.rename_rule = None

        mock_task_service.get_enabled_tasks.return_value = [mock_task]
        mock_match_task.return_value = mock_task
        # 當沒有重命名規則時，回傳原始路徑
        mock_rename.return_value = "/downloads/關鍵字檔案.mp4"

        process_completed_download("/downloads/關鍵字檔案.mp4")

        # 移動操作應使用 rename 回傳的路徑
        mock_move.assert_called_once()
