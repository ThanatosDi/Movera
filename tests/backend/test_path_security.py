import os
import pytest
from pathlib import Path

from backend.utils.path_security import validate_path_within, sanitize_filename


class TestValidatePathWithin:
    """validate_path_within 路徑驗證測試"""

    def test_valid_path_returns_true(self, tmp_path):
        """正常路徑應回傳 True"""
        allowed = [str(tmp_path)]
        child = tmp_path / "subdir" / "file.txt"
        child.parent.mkdir(parents=True, exist_ok=True)
        child.touch()
        assert validate_path_within(str(child), allowed) is True

    def test_path_traversal_returns_false(self, tmp_path):
        """含 .. 路徑穿越應回傳 False"""
        allowed = [str(tmp_path / "safe")]
        # 嘗試逃離 safe 目錄
        malicious = str(tmp_path / "safe" / ".." / "secret.txt")
        assert validate_path_within(malicious, allowed) is False

    def test_path_outside_allowed_returns_false(self, tmp_path):
        """路徑不在允許範圍內應回傳 False"""
        allowed = [str(tmp_path / "allowed")]
        outside = str(tmp_path / "forbidden" / "file.txt")
        assert validate_path_within(outside, allowed) is False

    def test_multiple_allowed_bases(self, tmp_path):
        """支援多個允許的基底目錄"""
        base_a = tmp_path / "a"
        base_b = tmp_path / "b"
        base_a.mkdir()
        base_b.mkdir()
        allowed = [str(base_a), str(base_b)]
        assert validate_path_within(str(base_b / "file.txt"), allowed) is True

    def test_path_object_input(self, tmp_path):
        """支援 Path 物件輸入"""
        allowed = [tmp_path]
        child = tmp_path / "file.txt"
        assert validate_path_within(child, allowed) is True


class TestSanitizeFilename:
    """sanitize_filename 檔名驗證測試"""

    def test_normal_filename_passes(self):
        """正常檔名應通過驗證"""
        result = sanitize_filename("Episode 01.mkv")
        assert result == "Episode 01.mkv"

    def test_filename_with_dot_dot_slash_raises(self):
        """含 ../ 的檔名應引發錯誤"""
        with pytest.raises(ValueError):
            sanitize_filename("../../etc/passwd")

    def test_filename_with_forward_slash_raises(self):
        """含 / 的檔名應引發錯誤"""
        with pytest.raises(ValueError):
            sanitize_filename("subdir/file.mkv")

    def test_filename_with_backslash_raises(self):
        """含 \\ 的檔名應引發錯誤"""
        with pytest.raises(ValueError):
            sanitize_filename("subdir\\file.mkv")

    def test_filename_with_dot_dot_raises(self):
        """含 .. 的檔名應引發錯誤"""
        with pytest.raises(ValueError):
            sanitize_filename("..file.txt/../evil")

    def test_empty_string_raises(self):
        """空字串應引發錯誤"""
        with pytest.raises(ValueError):
            sanitize_filename("")
