"""
安全格式字串替換工具模組單元測試
"""

from backend.utils.safe_format import safe_format


class TestSafeFormat:
    """測試 safe_format 函式"""

    def test_normal_key_replacement(self):
        """測試正常 {key} 替換"""
        result = safe_format("{title} - S01E{episode}.mp4", {"title": "動畫", "episode": "01"})
        assert result == "動畫 - S01E01.mp4"

    def test_attribute_access_not_replaced(self):
        """測試 {key.attr} 語法不被替換"""
        result = safe_format("{title.__class__}", {"title": "動畫"})
        assert result == "{title.__class__}"

    def test_index_access_not_replaced(self):
        """測試 {key[0]} 語法不被替換"""
        result = safe_format("{title[0]}", {"title": "動畫"})
        assert result == "{title[0]}"

    def test_unknown_key_preserved(self):
        """測試未匹配的 key 保留原始佔位符"""
        result = safe_format("{title} - {unknown}", {"title": "動畫"})
        assert result == "動畫 - {unknown}"

    def test_empty_mapping(self):
        """測試空 mapping"""
        result = safe_format("{title}", {})
        assert result == "{title}"

    def test_no_placeholders(self):
        """測試無佔位符的字串"""
        result = safe_format("plain text", {"key": "value"})
        assert result == "plain text"

    def test_multiple_same_key(self):
        """測試同一 key 出現多次"""
        result = safe_format("{ep} and {ep}", {"ep": "01"})
        assert result == "01 and 01"
