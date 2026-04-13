"""
環境變數設定解析模組單元測試
"""

from unittest.mock import patch

from backend.utils.env_config import (
    get_allow_webui_setting,
    get_env_allowed_directories,
    get_env_allowed_source_directories,
)


class TestGetEnvAllowedDirectories:
    """測試 get_env_allowed_directories 函式"""

    @patch.dict("os.environ", {"ALLOWED_DIRECTORIES": "/downloads,/media"})
    def test_parse_comma_separated(self):
        """測試解析逗號分隔的絕對路徑"""
        result = get_env_allowed_directories()
        assert result == ["/downloads", "/media"]

    @patch.dict("os.environ", {}, clear=True)
    def test_env_not_set_returns_empty(self):
        """測試環境變數未設定時回傳空陣列"""
        result = get_env_allowed_directories()
        assert result == []

    @patch.dict("os.environ", {"ALLOWED_DIRECTORIES": ""})
    def test_empty_string_returns_empty(self):
        """測試環境變數為空字串時回傳空陣列"""
        result = get_env_allowed_directories()
        assert result == []

    @patch.dict("os.environ", {"ALLOWED_DIRECTORIES": "/downloads,relative/path,/media"})
    def test_ignores_relative_paths(self):
        """測試忽略相對路徑，僅保留絕對路徑"""
        result = get_env_allowed_directories()
        assert result == ["/downloads", "/media"]

    @patch.dict("os.environ", {"ALLOWED_DIRECTORIES": " /downloads , /media "})
    def test_trims_whitespace(self):
        """測試自動去除前後空白"""
        result = get_env_allowed_directories()
        assert result == ["/downloads", "/media"]


class TestGetEnvAllowedSourceDirectories:
    """測試 get_env_allowed_source_directories 函式"""

    @patch.dict("os.environ", {"ALLOWED_SOURCE_DIRECTORIES": "/downloads,/media"})
    def test_parse_comma_separated(self):
        """測試解析逗號分隔的絕對路徑"""
        result = get_env_allowed_source_directories()
        assert result == ["/downloads", "/media"]

    @patch.dict("os.environ", {}, clear=True)
    def test_env_not_set_returns_empty(self):
        """測試環境變數未設定時回傳空陣列"""
        result = get_env_allowed_source_directories()
        assert result == []


class TestGetAllowWebuiSetting:
    """測試 get_allow_webui_setting 函式"""

    @patch.dict("os.environ", {"ALLOW_WEBUI_SETTING": "false"})
    def test_false_returns_false(self):
        """測試設為 false 時回傳 False"""
        assert get_allow_webui_setting() is False

    @patch.dict("os.environ", {"ALLOW_WEBUI_SETTING": "False"})
    def test_case_insensitive(self):
        """測試大小寫不敏感"""
        assert get_allow_webui_setting() is False

    @patch.dict("os.environ", {"ALLOW_WEBUI_SETTING": "true"})
    def test_true_returns_true(self):
        """測試設為 true 時回傳 True"""
        assert get_allow_webui_setting() is True

    @patch.dict("os.environ", {}, clear=True)
    def test_not_set_returns_true(self):
        """測試未設定時回傳 True（預設）"""
        assert get_allow_webui_setting() is True
