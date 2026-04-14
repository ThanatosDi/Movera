"""
Utils rename 模組單元測試
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from backend.utils.rename import Rename, ParseRenameRule, RegexRenameRule, apply_episode_offset


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

    def test_parse_rename_with_path_object(self, tmp_path):
        """測試以 Path 物件呼叫 ParseRenameRule，應正常運作"""
        src_file = tmp_path / "動畫名稱 - 01.mp4"
        src_file.write_text("test")

        rule = ParseRenameRule(
            filepath=src_file,  # Path 物件，非 str
            src="{title} - {episode}.mp4",
            dst="{title} - S01E{episode}.mp4",
        )

        result = rule.rename()

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

    def test_regex_rename_with_path_object(self, tmp_path):
        """測試以 Path 物件呼叫 RegexRenameRule，應正常運作"""
        src_file = tmp_path / "動畫名稱 - 01.mp4"
        src_file.write_text("test")

        rule = RegexRenameRule(
            filepath=src_file,  # Path 物件，非 str
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


class TestApplyEpisodeOffset:
    """測試 apply_episode_offset 函式"""

    def test_positive_offset_with_zero_padding(self):
        """測試正向偏移並保持零填充（"01" + 12 = "13"）"""
        assert apply_episode_offset("01", 12) == "13"

    def test_positive_offset_three_digit_padding(self):
        """測試三位數零填充（"003" + 10 = "013"）"""
        assert apply_episode_offset("003", 10) == "013"

    def test_offset_exceeds_original_width(self):
        """測試偏移後超出原始位數（"99" + 5 = "104"）"""
        assert apply_episode_offset("99", 5) == "104"

    def test_negative_offset(self):
        """測試負數偏移量（"13" + (-5) = "08"）"""
        assert apply_episode_offset("13", -5) == "08"

    def test_decimal_episode_with_offset(self):
        """測試小數 episode 值偏移（"07.5" + 12 = "19.5"）"""
        assert apply_episode_offset("07.5", 12) == "19.5"

    def test_decimal_episode_no_padding(self):
        """測試小數 episode 值無零填充（"7.5" + 5 = "12.5"）"""
        assert apply_episode_offset("7.5", 5) == "12.5"

    def test_non_numeric_value_returns_original(self):
        """測試非數字 group 值時回傳原始值"""
        assert apply_episode_offset("abc", 10) == "abc"

    def test_zero_offset(self):
        """測試偏移量為 0 時不改變值"""
        assert apply_episode_offset("05", 0) == "05"

    def test_single_digit_no_padding(self):
        """測試無零填充的單位數（"5" + 3 = "8"）"""
        assert apply_episode_offset("5", 3) == "8"


class TestRenameWithEpisodeOffset:
    """測試 Rename 類別整合 episode 偏移"""

    def test_parse_mode_with_offset(self, tmp_path):
        """測試 Parse 模式正向偏移"""
        src_file = tmp_path / "動畫 - 01.mp4"
        src_file.write_text("test")

        rename = Rename(
            filepath=str(src_file),
            src="{title} - {episode}.mp4",
            dst="{title} - S02E{episode}.mp4",
            rule="parse",
            episode_offset_enabled=True,
            episode_offset_group="episode",
            episode_offset_value=12,
        )

        result = rename.execute_rename()

        expected_path = tmp_path / "動畫 - S02E13.mp4"
        assert expected_path.exists()

    def test_regex_mode_with_offset(self, tmp_path):
        """測試 Regex 模式正向偏移（使用 named group）"""
        src_file = tmp_path / "動畫 - 01.mp4"
        src_file.write_text("test")

        rename = Rename(
            filepath=str(src_file),
            src=r"(?P<title>.+) - (?P<episode>\d+)\.mp4",
            dst=r"\g<title> - S02E\g<episode>.mp4",
            rule="regex",
            episode_offset_enabled=True,
            episode_offset_group="episode",
            episode_offset_value=12,
        )

        result = rename.execute_rename()

        expected_path = tmp_path / "動畫 - S02E13.mp4"
        assert expected_path.exists()

    def test_offset_disabled_no_effect(self, tmp_path):
        """測試偏移未啟用時不影響重新命名流程"""
        src_file = tmp_path / "動畫 - 01.mp4"
        src_file.write_text("test")

        rename = Rename(
            filepath=str(src_file),
            src="{title} - {episode}.mp4",
            dst="{title} - S01E{episode}.mp4",
            rule="parse",
            episode_offset_enabled=False,
            episode_offset_group="episode",
            episode_offset_value=12,
        )

        result = rename.execute_rename()

        expected_path = tmp_path / "動畫 - S01E01.mp4"
        assert expected_path.exists()

    def test_offset_without_params_backward_compatible(self, tmp_path):
        """測試不傳遞偏移參數時向後相容"""
        src_file = tmp_path / "動畫 - 01.mp4"
        src_file.write_text("test")

        rename = Rename(
            filepath=str(src_file),
            src="{title} - {episode}.mp4",
            dst="{title} - S01E{episode}.mp4",
            rule="parse",
        )

        result = rename.execute_rename()

        expected_path = tmp_path / "動畫 - S01E01.mp4"
        assert expected_path.exists()
