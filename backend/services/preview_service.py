import datetime

from parse import parse

from backend.utils.safe_format import safe_format
from backend.utils.safe_regex import safe_compile, safe_search, safe_sub


class ParsePreviewService:
    """Preview the result of a parse-template rename without touching the filesystem.

    Why: Users need instant feedback on their naming pattern before committing
    to a task. This service runs the parse library in a read-only fashion so
    the frontend can show a live preview.
    """

    @staticmethod
    def _match(pattern: str, text: str) -> dict | None:
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
    def _format(format_str: str, groups: dict) -> str:
        """使用指定的格式化字串和分組資料產生新的字串。

        參數:
            format_str (str): 用於產生新字串的格式化字串。
            groups (dict): 包含用於格式化的分組資料。

        回傳:
            str: 使用分組資料格式化後的字串。
        """
        return safe_format(format_str, groups)

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
        groups = ParsePreviewService._match(src_pattern, text)

        response = {
            "src_pattern": src_pattern,
            "text": text,
            "dst_pattern": dst_pattern,
        }

        if groups is None:
            return {**response, "groups": {}, "formatted": ""}

        formatted = ParsePreviewService._format(dst_pattern, groups)

        return {**response, "groups": groups, "formatted": formatted}


class RegexPreviewService:
    """Preview the result of a regex-based rename without touching the filesystem.

    Why: Regex patterns are error-prone; a live preview lets users verify
    named/numbered capture groups and substitution output before saving.
    """

    @staticmethod
    def _match(pattern: str, text: str) -> dict | None:
        """根據指定的正則表達式模式匹配文字，並回傳匹配結果。

        參數:
            pattern (str): 用於匹配的正則表達式模式字串。
            text (str): 要被匹配的文字。

        回傳:
            dict | None: 包含 named_group 和 numbered_group 的字典。
        """
        compiled = safe_compile(pattern)
        match = safe_search(compiled, text)
        named_group = match.groupdict() if match else {}
        numbered_group = list(match.groups()) if match else []
        return {"named_group": named_group, "numbered_group": numbered_group}

    @staticmethod
    def _format(
        src_pattern: str,
        text: str,
        dst_pattern: str,
    ) -> str:
        """
        使用指定的正則表達式模式和替換字串產生新的字串。
        參數:
            src_pattern (str): 用於匹配的正則表達式模式字串。
            text (str): 要被替換的文字。
            dst_pattern (str): 用於產生新字串的替換字串。
        回傳:
            str: 使用替換字串產生的新字串。
        """
        compiled = safe_compile(src_pattern)
        return safe_sub(compiled, dst_pattern, text)

    @staticmethod
    def preview(
        src_pattern: str,
        text: str,
        dst_pattern: str,
    ) -> dict:
        groups = RegexPreviewService._match(src_pattern, text)
        response = {
            "src_pattern": src_pattern,
            "text": text,
            "dst_pattern": dst_pattern,
        }
        if groups is None:
            return {**response, "groups": {}, "formatted": ""}

        formatted = RegexPreviewService._format(
            src_pattern,
            text,
            dst_pattern,
        )

        return {**response, "groups": groups, "formatted": formatted}
