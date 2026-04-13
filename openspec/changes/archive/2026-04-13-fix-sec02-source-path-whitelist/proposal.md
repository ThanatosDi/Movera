## Why

目前 Webhook 端點接收的 `filepath` 參數沒有任何來源路徑驗證，攻擊者可以透過偽造 Webhook 請求傳入任意檔案路徑（如 `/etc/passwd`），觸發 Worker 對系統敏感檔案執行搬移或重新命名操作。此問題在資安審查報告中被列為 SEC-02（CRITICAL 等級）。需要新增「檔案來源白名單」設定，讓管理者明確指定哪些目錄下的檔案允許被 Worker 處理。

## What Changes

- 新增 `allowed_source_directories` 系統設定項（JSON 陣列，儲存絕對路徑清單）
- 在設定頁面新增「檔案來源白名單」區塊，提供 UI 讓使用者管理允許的來源目錄
- Worker 在處理 Webhook 傳入的檔案路徑前，驗證該路徑是否位於白名單範圍內
- 白名單為空時允許所有路徑（向後相容，不影響現有使用者）

## Capabilities

### New Capabilities
- `source-path-whitelist`: 檔案來源路徑白名單機制，涵蓋後端設定存取、Worker 路徑驗證、以及前端設定頁面 UI

### Modified Capabilities
<!-- 無既有 spec 層級的行為變更 -->

## Impact

- **後端**：`SettingService`（新增 JSON 欄位與存取方法）、`worker.py`（新增路徑驗證邏輯）、`WorkerServices`（新增 `SettingService` 依賴）
- **前端**：設定頁面（新增白名單管理區塊 UI）
- **API**：使用既有的 `PUT /api/v1/settings` 端點，無需新增 API
- **資料庫**：無 schema 變更，透過既有的 key-value 設定表存放新設定項
