"""
Utils rename 模組單元測試
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from backend.utils.rename import Rename, ParseRenameRule, RegexRenameRule


class TestParseRenameRule:
    """測試 ParseRenameRule 類別"""

    def test_parse_rename_success(self, tmp_path):
        """測試成功使用 parse 規則重命名"""
        # 建立測試檔案
        src_file = tmp_path / "動畫名稱 - 01.mp4"
        src_file.write_text("test")

        rule = ParseRenameRule(
            filepath=str(src_file),
            src="{title} - {episode}.mp4",
            dst="{title} - S01E{episode}.mp4",
        )

        result = rule.rename()

        # 驗證重命名結果
        expected_path = tmp_path / "動畫名稱 - S01E01.mp4"
        assert expected_path.exists()
        assert not src_file.exists()

    def test_parse_rename_with_multiple_groups(self, tmp_path):
        """測試多個群組的 parse 規則"""
        src_file = tmp_path / "Show Name - Episode Title - 05.mp4"
        src_file.write_text("test")

        rule = ParseRenameRule(
            filepath=str(src_file),
            src="{show} - {ep_title} - {num}.mp4",
            dst="{show} S01E{num} - {ep_title}.mp4",
        )

        result = rule.rename()

        expected_path = tmp_path / "Show Name S01E05 - Episode Title.mp4"
        assert expected_path.exists()


class TestRegexRenameRule:
    """測試 RegexRenameRule 類別"""

    def test_regex_rename_success(self, tmp_path):
        """測試成功使用 regex 規則重命名"""
        src_file = tmp_path / "動畫名稱 - 01.mp4"
        src_file.write_text("test")

        rule = RegexRenameRule(
            filepath=str(src_file),
            src=r"(.+) - (\d+)\.mp4",
            dst=r"\1 - S01E\2.mp4",
        )

        result = rule.rename()

        expected_path = tmp_path / "動畫名稱 - S01E01.mp4"
        assert expected_path.exists()
        assert not src_file.exists()

    def test_regex_rename_case_insensitive(self, tmp_path):
        """測試大小寫不敏感"""
        src_file = tmp_path / "ANIME - 01.MP4"
        src_file.write_text("test")

        rule = RegexRenameRule(
            filepath=str(src_file),
            src=r"anime - (\d+)\.mp4",
            dst=r"Anime - S01E\1.mp4",
        )

        result = rule.rename()

        expected_path = tmp_path / "Anime - S01E01.mp4"
        assert expected_path.exists()

    def test_regex_rename_with_optional_group(self, tmp_path):
        """測試可選群組"""
        src_file = tmp_path / "動畫 - 01v2 [1080P].mp4"
        src_file.write_text("test")

        rule = RegexRenameRule(
            filepath=str(src_file),
            src=r"(.+) - (\d+)(v\d+)? \[(.+)\]\.mp4",
            dst=r"\1 - S01E\2 [\4].mp4",
        )

        result = rule.rename()

        expected_path = tmp_path / "動畫 - S01E01 [1080P].mp4"
        assert expected_path.exists()


class TestRename:
    """測試 Rename 類別"""

    def test_rename_with_regex_rule(self, tmp_path):
        """測試使用 regex 規則"""
        src_file = tmp_path / "test - 01.mp4"
        src_file.write_text("test")

        rename = Rename(
            filepath=str(src_file),
            src=r"(.+) - (\d+)\.mp4",
            dst=r"\1 - S01E\2.mp4",
            rule="regex",
        )

        result = rename.execute_rename()

        expected_path = tmp_path / "test - S01E01.mp4"
        assert expected_path.exists()

    def test_rename_with_parse_rule(self, tmp_path):
        """測試使用 parse 規則"""
        src_file = tmp_path / "test - 01.mp4"
        src_file.write_text("test")

        rename = Rename(
            filepath=str(src_file),
            src="{title} - {episode}.mp4",
            dst="{title} - S01E{episode}.mp4",
            rule="parse",
        )

        result = rename.execute_rename()

        expected_path = tmp_path / "test - S01E01.mp4"
        assert expected_path.exists()

    def test_rename_invalid_rule(self, tmp_path):
        """測試無效的規則類型"""
        src_file = tmp_path / "test.mp4"
        src_file.write_text("test")

        rename = Rename(
            filepath=str(src_file),
            src="pattern",
            dst="result",
            rule="invalid_rule",
        )

        with pytest.raises(ValueError) as exc_info:
            rename.execute_rename()

        assert "未知的重新命名規則類型" in str(exc_info.value)

    def test_rename_rule_case_insensitive(self, tmp_path):
        """測試規則類型大小寫不敏感"""
        src_file = tmp_path / "test - 01.mp4"
        src_file.write_text("test")

        rename = Rename(
            filepath=str(src_file),
            src=r"(.+) - (\d+)\.mp4",
            dst=r"\1 - S01E\2.mp4",
            rule="REGEX",  # 大寫
        )

        result = rename.execute_rename()

        expected_path = tmp_path / "test - S01E01.mp4"
        assert expected_path.exists()

    def test_rename_returns_new_path(self, tmp_path):
        """測試回傳新的檔案路徑"""
        src_file = tmp_path / "original.mp4"
        src_file.write_text("test")

        rename = Rename(
            filepath=str(src_file),
            src=r"original\.mp4",
            dst="renamed.mp4",
            rule="regex",
        )

        result = rename.execute_rename()

        # 驗證回傳的是新路徑
        assert result == tmp_path / "renamed.mp4"
