## Why

SEC-10：`backend/utils/rename.py:34` 和 `backend/services/preview_service.py:49` 使用 `str.format(**dict)` 搭配使用者控制的格式字串。Python 的 `str.format()` 可以透過 `{0.__class__.__init__.__globals__}` 等語法存取物件屬性，可能導致敏感資訊洩漏。

## What Changes

- 新增 `safe_format()` 工具函式，僅允許簡單的 `{key}` 替換，禁止屬性存取（`{key.attr}`）和索引存取（`{key[0]}`）
- 替換 `rename.py` 和 `preview_service.py` 中的 `str.format()` 為 `safe_format()`

## Capabilities

### New Capabilities

### Modified Capabilities

## Impact

- **後端**：`backend/utils/rename.py`、`backend/services/preview_service.py`、新增工具函式
- **前端**：無修改
- **行為變更**：使用者的格式字串如包含 `{key.attr}` 等進階語法，將無法執行（回傳原始佔位符）
