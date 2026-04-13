"""安全格式字串替換工具。

Why: Python 的 str.format() 可透過 {key.__class__} 等語法存取物件屬性，
造成資訊洩漏風險。此模組僅支援 {key} 簡單替換，禁止屬性存取和索引存取。
"""

import re

# 匹配簡單的 {key}（key 僅由字母、數字、底線組成，不含 .、[、!、: 等）
_SIMPLE_PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


def safe_format(template: str, mapping: dict) -> str:
    """安全的格式字串替換，僅支援 {key} 簡單佔位符。

    不支援 {key.attr}、{key[0]}、{key!r}、{key:format} 等進階語法。
    未匹配的 key 保留原始佔位符。
    """
    def replacer(match: re.Match) -> str:
        key = match.group(1)
        if key in mapping:
            return str(mapping[key])
        return match.group(0)

    return _SIMPLE_PLACEHOLDER.sub(replacer, template)
