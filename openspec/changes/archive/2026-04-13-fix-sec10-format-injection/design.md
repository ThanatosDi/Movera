## Context

兩處 `str.format(**dict)` 呼叫：
1. `ParseRenameRule.rename()` — `self.dst.format(**template.named)`，`template.named` 來自 `parse.parse()` 的結果，值為字串
2. `ParsePreviewService._format()` — `format_str.format(**groups)`，`groups` 來自 parse 結果，值也是字串

風險在於 `self.dst`（目標格式字串）和 `format_str` 都由使用者控制。雖然 dict 的值是字串，但 Python `str.format()` 可以透過 `{key.__class__}` 語法存取值物件的屬性。

## Goals / Non-Goals

**Goals:**
- 替換為安全的格式化函式，僅支援 `{key}` 簡單替換
- 維持現有的 parse 功能不變

**Non-Goals:**
- 不修改 regex rename/preview（已使用 `re.sub` 替換機制，不涉及 `str.format()`）

## Decisions

### 1. 使用 `string.Template` 風格的手動替換

**選擇：** 自行實作 `safe_format(template, mapping)`，用正則表達式匹配 `{key}` 並從 mapping 中取值替換。不接受 `{key.attr}`、`{key[0]}`、`{key!r}` 等進階語法。

**理由：**
- `string.Template` 使用 `$key` 語法，與現有 `{key}` 不相容
- 自行實作最簡單，完全控制行為，不引入新依賴

**替代方案：** 使用 `string.Formatter` 子類別覆寫 `get_field()`——被否決，過於複雜。
