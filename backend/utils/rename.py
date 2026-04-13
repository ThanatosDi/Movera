from pathlib import Path
from typing import Literal

import parse

from backend.utils.safe_format import safe_format
from backend.utils.safe_regex import safe_compile, safe_sub


def _ensure_path(filepath: str | Path) -> Path:
    """將 filepath 統一轉換為 Path 物件。

    Why: ParseRenameRule 與 RegexRenameRule 都需要處理 str 或 Path 兩種輸入，
    提取為共用函式避免重複邏輯並防止變數作用域錯誤。
    """
    return Path(filepath) if isinstance(filepath, str) else filepath


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
    ):
        """初始化重新命名處理程序。

        :param filepath: 待重新命名的檔案路徑
        :param src: 原始檔案名稱比對規則
        :param dst: 重新命名後的檔案名稱規則
        :param rule: 規則類型，"regex" 或 "parse"
        """
        super().__init__(filepath=filepath, src=src, dst=dst)
        self.rule_type = rule.lower()

    def execute_rename(self) -> Path:
        """根據 rule_type 分派至對應的重新命名方法。

        :return: 重新命名後的檔案路徑
        :raises ValueError: rule_type 不是 `regex` 或 `parse` 時拋出
        """
        if self.rule_type == "regex":
            return RegexRenameRule.rename(self)
        elif self.rule_type == "parse":
            return ParseRenameRule.rename(self)
        else:
            raise ValueError(f"未知的重新命名規則類型: {self.rule_type}")
