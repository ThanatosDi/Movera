## Why

SEC-08：目錄掃描時未檢查 symlink，攻擊者可在允許目錄內建立符號連結指向敏感路徑（如 `/etc`），繞過存取控制。

SEC-11：所有 Pydantic schema 的 `str` 欄位都沒有 `max_length` 限制，攻擊者可發送超長字串造成記憶體耗盡或處理延遲。

## What Changes

- **SEC-08**：在 `DirectoryService` 的 `_scan_directories()` 和 `_has_subdirectories()` 中加入 `is_symlink()` 檢查，跳過符號連結
- **SEC-11**：為所有 Pydantic schema 的 `str` 欄位加入合理的 `max_length` 限制

## Capabilities

### New Capabilities

### Modified Capabilities

## Impact

- **後端**：`backend/services/directory_service.py`（symlink 過濾）、`backend/schemas.py`（max_length 限制）
- **前端**：無修改
- **API**：超長字串的請求會被 Pydantic 驗證拒絕（422 錯誤）
