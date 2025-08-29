import re
from pathlib import Path
from typing import Literal

import parse


class ParseRenameRule:
    """
    使用字串解析規則重新命名檔案。
    """

    def __init__(self, filepath: str, src: str, dst: str):
        self.filepath = filepath
        self.src = src
        self.dst = dst

    def rename(self) -> str:
        if isinstance(self.filepath, str):
            filepath = Path(self.filepath)
        filename = filepath.name
        template = parse.parse(self.src, filename)
        renamed = self.dst.format(**template.named)
        dst_path = filepath.parent.joinpath(renamed)
        return Path.rename(filepath, dst_path)


class RegexRenameRule:
    """
    使用正則表達式規則重新命名檔案。
    """

    def __init__(self, filepath: str, src: str, dst: str):
        self.filepath = filepath
        self.src = src
        self.dst = dst

    def rename(self) -> str:
        if isinstance(self.filepath, str):
            filepath = Path(self.filepath)
        filename = filepath.name
        src_filename_regex = re.compile(self.src, re.IGNORECASE)
        renamed = re.sub(src_filename_regex, self.dst, filename)
        dst_path = filepath.parent.joinpath(renamed)
        return Path.rename(filepath, dst_path)


class Rename(RegexRenameRule, ParseRenameRule):
    """
    重新命名處理程序的主類別。
    根據任務設定的規則，分派給對應的重新命名方法。
    """

    def __init__(
        self,
        filepath: str,
        src: str,
        dst: str,
        rule: str = Literal["regex", "parse"],
    ):
        """
        重新命名處理程序的初始化方法

        :param src: 原始檔案名稱規則
        :param dst: 欲重新命名後的檔案名稱規則
        :param rule: 重新命名規則的類型，"regex" 或 "parse"
        """
        super().__init__(filepath=filepath, src=src, dst=dst)
        self.rule_type = rule.lower()

    def execute_rename(self) -> str:
        """
        執行重新命名處理，根據 rule_type 的值，分派給對應的重新命名方法。

        :return: 重新命名後的檔案路徑
        :raises ValueError: 如果 **rule_type** 的值不是 `regex` 或 `parse`，就拋出ValueError
        """
        if self.rule_type == "regex":
            # 呼叫 RegexRenameRule 的 rename 方法
            return RegexRenameRule.rename(self)
        elif self.rule_type == "parse":
            # 呼叫 ParseRenameRule 的 rename 方法
            return ParseRenameRule.rename(self)
        else:
            raise ValueError(f"未知的重新命名規則類型: {self.rule_type}")
