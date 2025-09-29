import datetime

from parse import parse


class ParsePreviewService:
    @staticmethod
    def __match(self, pattern: str, text: str) -> dict | None:
        """根據指定的模式解析文字，並回傳解析結果。

        參數:
            pattern (str): 用於解析的模式字串。
            text (str): 要被解析的文字。

        回傳:
            dict | None: 如果解析成功，回傳包含解析後的分組 (groups) 的字典；否則回傳 None。
        """
        result = parse(pattern, text)
        if not result:
            return None

        groups = result.named
        for key, value in groups.items():
            if isinstance(value, datetime.datetime):
                groups[key] = str(value)

        return groups

    @staticmethod
    def __format(self, format_str: str, groups: dict) -> str:
        """使用指定的格式化字串和分組資料產生新的字串。

        參數:
            format_str (str): 用於產生新字串的格式化字串。
            groups (dict): 包含用於格式化的分組資料。

        回傳:
            str: 使用分組資料格式化後的字串。
        """
        return format_str.format(**groups)

    @staticmethod
    def preview(
        src_pattern: str,
        text: str,
        dst_pattern: str,
    ) -> dict:
        """根據指定的模式解析文字，並使用另一個格式化字串產生預覽結果。

        參數:
            src_pattern (str): 用於解析的模式字串。
            text (str): 要被解析的文字。
            dst_pattern (str): 用於產生新字串的格式化字串。

        回傳:
            dict: 包含解析後的分組 (groups) 與格式化後字串 (formatted) 的字典。
        """
        groups = ParsePreviewService.__match(src_pattern, text)

        response = {
            "src_pattern": src_pattern,
            "text": text,
            "dst_pattern": dst_pattern,
        }

        if groups is None:
            return {**response, "groups": {}, "formatted": ""}

        formatted = ParsePreviewService.__format(dst_pattern, groups)

        return {**response, "groups": groups, "formatted": formatted}
