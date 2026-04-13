"""
安全正則表達式工具模組單元測試
"""

import re

import pytest

from backend.utils.safe_regex import (
    RegexTimeoutError,
    safe_compile,
    safe_search,
    safe_sub,
)


class TestSafeCompile:
    """測試 safe_compile 函式"""

    def test_normal_pattern_compiles(self):
        """測試正常 pattern 回傳 compiled pattern"""
        pattern = safe_compile(r"(.+) - (\d+)\.mp4")
        assert isinstance(pattern, re.Pattern)

    def test_pattern_exceeds_max_length_raises(self):
        """測試超過長度限制時拋出 ValueError"""
        long_pattern = "a" * 501
        with pytest.raises(ValueError, match="長度超過上限"):
            safe_compile(long_pattern, max_length=500)

    def test_pattern_at_max_length_ok(self):
        """測試剛好在長度限制內不拋出"""
        pattern = safe_compile("a" * 500, max_length=500)
        assert isinstance(pattern, re.Pattern)

    def test_invalid_pattern_raises(self):
        """測試無效正則表達式拋出 re.error"""
        with pytest.raises(re.error):
            safe_compile("[invalid")


class TestSafeSearch:
    """測試 safe_search 函式"""

    def test_normal_match_returns_match(self):
        """測試正常匹配回傳 Match 物件"""
        pattern = safe_compile(r"(\w+) - (\d+)")
        result = safe_search(pattern, "動畫 - 01 [1080P].mp4")
        assert result is not None
        assert result.group(1) == "動畫"
        assert result.group(2) == "01"

    def test_no_match_returns_none(self):
        """測試不匹配時回傳 None"""
        pattern = safe_compile(r"不存在的pattern")
        result = safe_search(pattern, "測試文字")
        assert result is None

    def test_timeout_raises_regex_timeout_error(self):
        """測試逾時時拋出 RegexTimeoutError"""
        # 使用已知會造成 catastrophic backtracking 的 pattern
        pattern = safe_compile(r"(a+)+b")
        with pytest.raises(RegexTimeoutError):
            safe_search(pattern, "a" * 30 + "c", timeout=1)


class TestSafeSub:
    """測試 safe_sub 函式"""

    def test_normal_sub_returns_result(self):
        """測試正常替換回傳結果字串"""
        pattern = safe_compile(r"(\w+) - (\d+)")
        result = safe_sub(pattern, r"\1 - S01E\2", "動畫 - 01 [1080P].mp4")
        assert result == "動畫 - S01E01 [1080P].mp4"

    def test_no_match_returns_original(self):
        """測試不匹配時回傳原始字串"""
        pattern = safe_compile(r"不存在")
        result = safe_sub(pattern, "替換", "原始文字")
        assert result == "原始文字"

    def test_timeout_raises_regex_timeout_error(self):
        """測試逾時時拋出 RegexTimeoutError"""
        pattern = safe_compile(r"(a+)+b")
        with pytest.raises(RegexTimeoutError):
            safe_sub(pattern, "replacement", "a" * 30 + "c", timeout=1)
