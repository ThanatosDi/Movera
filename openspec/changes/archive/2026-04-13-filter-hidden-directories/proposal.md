## Why

目錄選擇器目前只過濾 `.` 開頭的隱藏目錄，但 `#` 開頭（如 `#recycle`、`#snapshot`）和 `@` 開頭（如 `@eaDir`、`@tmp`）的系統/暫存目錄在 NAS 環境中很常見（Synology DSM 等），這些目錄不應出現在使用者的目錄瀏覽清單中。

## What Changes

- 擴展 `DirectoryService` 的目錄過濾邏輯，排除 `.`、`#`、`@` 開頭的資料夾
- 提取過濾條件為共用函式，避免重複

## Capabilities

### New Capabilities

### Modified Capabilities

## Impact

- **後端**：`backend/services/directory_service.py`（`_scan_directories` 和 `_has_subdirectories` 兩處）
- **前端**：無修改
- **API**：`GET /api/v1/directories` 回傳結果會過濾掉更多系統目錄
