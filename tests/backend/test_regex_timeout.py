import pytest
import re

from backend.services.preview_service import RegexPreviewService


class TestRegexTimeout:
    """Regex 超時防護測試"""

    def test_normal_pattern_completes(self):
        """正常 regex pattern 在限時內完成"""
        result = RegexPreviewService._match(r"(\d+)", "file_123.mkv")
        assert result is not None

    def test_normal_format_completes(self):
        """正常 regex format 在限時內完成"""
        result = RegexPreviewService._format(r"file_(\d+)\.mkv", "file_123.mkv", r"ep_\1.mkv")
        assert result == "ep_123.mkv"

    def test_malicious_pattern_raises_timeout(self):
        """惡意 regex pattern 超時應引發錯誤"""
        # 經典 ReDoS pattern
        evil_pattern = r"(a+)+$"
        evil_input = "a" * 30 + "!"
        with pytest.raises((TimeoutError, re.error)):
            RegexPreviewService._match(evil_pattern, evil_input)

    def test_malicious_format_raises_timeout(self):
        """惡意 regex format 超時應引發錯誤"""
        evil_pattern = r"(a+)+$"
        evil_input = "a" * 30 + "!"
        with pytest.raises((TimeoutError, re.error)):
            RegexPreviewService._format(evil_pattern, evil_input, r"\1")
