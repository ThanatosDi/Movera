"""驗證所有 Backend 模組遵循 snake_case 命名慣例"""


class TestServiceModuleNaming:
    """驗證 Service 模組可從 snake_case 路徑匯入"""

    def test_import_task_service(self):
        from backend.services.task_service import TaskService
        assert TaskService is not None

    def test_import_setting_service(self):
        from backend.services.setting_service import SettingService
        assert SettingService is not None

    def test_import_preview_service(self):
        from backend.services.preview_service import ParsePreviewService, RegexPreviewService
        assert ParsePreviewService is not None
        assert RegexPreviewService is not None

    def test_import_path_service(self):
        from backend.services.directory_service import DirectoryService
        assert DirectoryService is not None

    def test_import_log_service(self):
        from backend.services.log_service import LogService
        assert LogService is not None


class TestExceptionModuleNaming:
    """驗證 Exception 模組可從 snake_case 路徑匯入"""

    def test_import_task_exception(self):
        from backend.exceptions.task_exception import TaskAlreadyExists, TaskNotFound
        assert TaskAlreadyExists is not None
        assert TaskNotFound is not None

    def test_import_directory_exception(self):
        from backend.exceptions.directory_exception import DirectoryAccessDenied, DirectoryNotFound
        assert DirectoryAccessDenied is not None
        assert DirectoryNotFound is not None

    def test_import_worker_exception(self):
        from backend.exceptions.worker_exception import RenameOperationError, MoveOperationError
        assert RenameOperationError is not None
        assert MoveOperationError is not None
