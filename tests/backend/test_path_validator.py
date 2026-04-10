"""路徑驗證工具函式單元測試"""

from backend.utils.path_validator import is_absolute_path, validate_allowed_directories


class TestIsAbsolutePath:
    """測試 is_absolute_path 函式"""

    def test_posix_absolute_path(self):
        assert is_absolute_path("/home/user/downloads") is True

    def test_windows_absolute_path(self):
        assert is_absolute_path("C:\\Users\\Downloads") is True

    def test_relative_path(self):
        assert is_absolute_path("downloads/files") is False

    def test_dot_relative_path(self):
        assert is_absolute_path("./downloads") is False


class TestValidateAllowedDirectories:
    """測試 validate_allowed_directories 函式"""

    def test_all_valid(self):
        dirs = ["/home/user", "C:\\Users"]
        assert validate_allowed_directories(dirs) == []

    def test_mixed_valid_invalid(self):
        dirs = ["/home/user", "relative/path", "C:\\Users"]
        assert validate_allowed_directories(dirs) == ["relative/path"]

    def test_all_invalid(self):
        dirs = ["relative", "./local"]
        assert validate_allowed_directories(dirs) == ["relative", "./local"]

    def test_empty_list(self):
        assert validate_allowed_directories([]) == []
