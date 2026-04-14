from pathlib import Path
from typing import Literal

import parse
from loguru import logger

from backend.utils.safe_format import safe_format
from backend.utils.safe_regex import safe_compile, safe_search, safe_sub


def _ensure_path(filepath: str | Path) -> Path:
    """將 filepath 統一轉換為 Path 物件。

    Why: ParseRenameRule 與 RegexRenameRule 都需要處理 str 或 Path 兩種輸入，
    提取為共用函式避免重複邏輯並防止變數作用域錯誤。
    """
    return Path(filepath) if isinstance(filepath, str) else filepath


def apply_episode_offset(value: str, offset: int) -> str:
    """對 episode 數值字串套用偏移量。

    支援整數（如 "01"）與小數（如 "07.5"）格式。
    偏移後保留原始零填充與小數部分。

    Args:
        value: 原始 episode 數值字串
        offset: 偏移量（整數）

    Returns:
        偏移後的數值字串，保留原始格式；若非數字則回傳原始值
    """
    if offset == 0:
        return value

    # 處理小數情況（如 "07.5"）
    if "." in value:
        parts = value.split(".", 1)
        int_part_str = parts[0]
        decimal_part = parts[1]

        try:
            int_val = int(int_part_str)
        except ValueError:
            logger.warning(
                f"Episode 偏移：群組值 '{value}' 的整數部分無法轉換為數字，跳過偏移"
            )
            return value

        new_int_val = int_val + offset
        # 保留零填充：取原始整數部分的位數
        original_width = len(int_part_str)
        new_int_str = str(new_int_val).zfill(original_width)
        return f"{new_int_str}.{decimal_part}"

    # 處理整數情況（如 "01"、"003"）
    try:
        int_val = int(value)
    except ValueError:
        logger.warning(f"Episode 偏移：群組值 '{value}' 無法轉換為數字，跳過偏移")
        return value

    new_val = int_val + offset
    original_width = len(value)
    return str(new_val).zfill(original_width)


class ParseRenameRule:
    """使用 parse 函式庫的字串樣板規則重新命名檔案。

    Why: 提供比正則表達式更直覺的命名模式語法（如 `{title} - {episode}`），
    適合非技術使用者定義重命名規則。
    """

    def __init__(self, filepath: str | Path, src: str, dst: str):
        self.filepath = filepath
        self.src = src
        self.dst = dst

    def rename(self) -> Path:
        filepath = _ensure_path(self.filepath)
        filename = filepath.name
        template = parse.parse(self.src, filename)
        renamed = safe_format(self.dst, template.named)
        dst_path = filepath.parent.joinpath(renamed)
        return Path.rename(filepath, dst_path)


class RegexRenameRule:
    """使用正則表達式規則重新命名檔案。

    Why: 提供完整的正則表達式能力，支援複雜的檔案名稱比對與替換場景，
    如可選群組、大小寫不敏感等進階需求。
    """

    def __init__(self, filepath: str | Path, src: str, dst: str):
        self.filepath = filepath
        self.src = src
        self.dst = dst

    def rename(self) -> Path:
        filepath = _ensure_path(self.filepath)
        filename = filepath.name
        src_filename_regex = safe_compile(self.src)
        renamed = safe_sub(src_filename_regex, self.dst, filename)
        dst_path = filepath.parent.joinpath(renamed)
        return Path.rename(filepath, dst_path)


class Rename(RegexRenameRule, ParseRenameRule):
    """根據任務設定的規則類型，分派至對應的重新命名策略。

    Why: 統一進入點讓 Worker 不需要判斷規則類型，
    由此類別負責策略選擇，符合開放封閉原則。
    """

    def __init__(
        self,
        filepath: str | Path,
        src: str,
        dst: str,
        rule: str = Literal["regex", "parse"],
        episode_offset_enabled: bool = False,
        episode_offset_group: str | None = None,
        episode_offset_value: int = 0,
    ):
        """初始化重新命名處理程序。

        :param filepath: 待重新命名的檔案路徑
        :param src: 原始檔案名稱比對規則
        :param dst: 重新命名後的檔案名稱規則
        :param rule: 規則類型，"regex" 或 "parse"
        :param episode_offset_enabled: 是否啟用 episode 偏移
        :param episode_offset_group: 偏移目標的 group 名稱
        :param episode_offset_value: episode 偏移量
        """
        super().__init__(filepath=filepath, src=src, dst=dst)
        self.rule_type = rule.lower()
        self.episode_offset_enabled = episode_offset_enabled
        self.episode_offset_group = episode_offset_group
        self.episode_offset_value = episode_offset_value

    def _should_apply_offset(self) -> bool:
        """判斷是否需要套用 episode 偏移。"""
        return (
            self.episode_offset_enabled
            and self.episode_offset_group is not None
            and self.episode_offset_value != 0
        )

    def _execute_parse_rename(self) -> Path:
        """Parse 模式重新命名，支援 episode 偏移。"""
        filepath = _ensure_path(self.filepath)
        filename = filepath.name
        template = parse.parse(self.src, filename)
        groups = dict(template.named)

        if self._should_apply_offset():
            group = self.episode_offset_group
            if group in groups:
                groups[group] = apply_episode_offset(
                    str(groups[group]), self.episode_offset_value
                )

        renamed = safe_format(self.dst, groups)
        dst_path = filepath.parent.joinpath(renamed)
        return Path.rename(filepath, dst_path)

    def _execute_regex_rename(self) -> Path:
        """Regex 模式重新命名，支援 episode 偏移。"""
        filepath = _ensure_path(self.filepath)
        filename = filepath.name
        dst = self.dst

        if self._should_apply_offset():
            src_regex = safe_compile(self.src)
            match = safe_search(src_regex, filename)
            if match:
                group_dict = match.groupdict()
                group = self.episode_offset_group
                if group in group_dict and group_dict[group] is not None:
                    offset_val = apply_episode_offset(
                        group_dict[group], self.episode_offset_value
                    )
                    # 將 dst 中的 named backreference 替換為偏移後的字面值
                    dst = dst.replace(f"\\g<{group}>", offset_val)

        src_regex = safe_compile(self.src)
        renamed = safe_sub(src_regex, dst, filename)
        dst_path = filepath.parent.joinpath(renamed)
        return Path.rename(filepath, dst_path)

    def execute_rename(self) -> Path:
        """根據 rule_type 分派至對應的重新命名方法。

        :return: 重新命名後的檔案路徑
        :raises ValueError: rule_type 不是 `regex` 或 `parse` 時拋出
        """
        if self.rule_type == "regex":
            if self._should_apply_offset():
                return self._execute_regex_rename()
            return RegexRenameRule.rename(self)
        elif self.rule_type == "parse":
            if self._should_apply_offset():
                return self._execute_parse_rename()
            return ParseRenameRule.rename(self)
        else:
            raise ValueError(f"未知的重新命名規則類型: {self.rule_type}")
