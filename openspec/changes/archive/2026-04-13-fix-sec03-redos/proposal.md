## Why

使用者提供的正則表達式直接傳入 Python `re.compile()` 和 `re.sub()`，沒有任何複雜度限制或逾時機制。惡意的正則表達式（如 `(a+)+b`）可造成指數級回溯（catastrophic backtracking），導致 CPU 耗盡、服務中斷。此問題在資安審查報告中被列為 SEC-03（CRITICAL 等級），是目前剩餘的最高優先修復項目。

## What Changes

- 新增安全的正則表達式執行工具函式，加入長度限制與逾時保護
- 替換 `backend/utils/rename.py` 中的 `re.compile()` / `re.sub()` 為安全版本
- 替換 `backend/services/preview_service.py` 中的 `re.compile()` / `re.search()` / `re.sub()` 為安全版本
- 正則表達式逾時或過長時回傳明確的錯誤訊息給前端
- 前端邏輯與 UI 不需修改（錯誤透過既有 API 錯誤處理機制回傳）

## Capabilities

### New Capabilities

### Modified Capabilities

## Impact

- **後端**：`backend/utils/rename.py`（RegexRenameRule）、`backend/services/preview_service.py`（RegexPreviewService）、新增安全正則表達式工具函式
- **前端**：無修改（錯誤透過既有 API error handling 顯示）
- **API**：Preview API 在正則表達式無效或逾時時回傳 400 錯誤
