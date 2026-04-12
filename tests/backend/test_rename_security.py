import pytest
from pathlib import Path

from backend.utils.rename import ParseRenameRule, RegexRenameRule


class TestRenamePathTraversal:
    """Rename 產出檔名路徑穿越防護測試"""

    def test_parse_rename_normal_filename(self, tmp_path):
        """ParseRenameRule 正常檔名重新命名成功"""
        test_file = tmp_path / "Show - EP01.mkv"
        test_file.write_bytes(b"data")
        rule = ParseRenameRule(
            filepath=str(test_file),
            src="{title} - {ep}.mkv",
            dst="{title}_{ep}.mkv",
        )
        result = rule.rename()
        assert result.name == "Show_EP01.mkv"

    def test_parse_rename_traversal_raises(self, tmp_path):
        """ParseRenameRule 產出含 ../ 的檔名應引發錯誤"""
        test_file = tmp_path / "Show - EP01.mkv"
        test_file.write_bytes(b"data")
        rule = ParseRenameRule(
            filepath=str(test_file),
            src="{title} - {ep}.mkv",
            dst="../../{title}_{ep}.mkv",
        )
        with pytest.raises(ValueError, match="路徑穿越"):
            rule.rename()

    def test_regex_rename_traversal_raises(self, tmp_path):
        """RegexRenameRule 產出含路徑分隔符的檔名應引發錯誤"""
        test_file = tmp_path / "show_ep01.mkv"
        test_file.write_bytes(b"data")
        rule = RegexRenameRule(
            filepath=str(test_file),
            src=r"(.+)_(.+)\.mkv",
            dst=r"subdir/\1_\2.mkv",
        )
        with pytest.raises(ValueError, match="路徑分隔符"):
            rule.rename()
