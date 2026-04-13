## Context

Movera 以 Docker 為主要部署方式。目前 `allowed_directories` 和 `allowed_source_directories` 只能透過 Web UI 管理，無法透過 `docker-compose.yml` 的 `environment` 區段預先配置。在容器化環境中，管理者需要能透過環境變數鎖定安全關鍵設定，防止前端使用者修改。

現有架構中 `SettingService` 負責所有設定的讀寫，設定儲存在 SQLite 的 key-value 表中。

## Goals / Non-Goals

**Goals:**
- 支援透過環境變數 `ALLOWED_DIRECTORIES` 和 `ALLOWED_SOURCE_DIRECTORIES` 注入目錄設定
- 環境變數項目與資料庫項目合併，環境變數項目不可被刪除
- 透過 `ALLOW_WEBUI_SETTING=false` 完全鎖定前端對這兩個設定的新增/修改能力
- API 層在鎖定時回傳 403 拒絕修改

**Non-Goals:**
- 不將其他設定（timezone、locale）納入環境變數控制
- 不修改資料庫 schema（環境變數項目不寫入資料庫，僅在執行階段合併）

## Decisions

### 1. 環境變數項目不寫入資料庫，執行階段合併

**選擇：** 環境變數在 `SettingService` 讀取時即時合併，不在啟動時寫入資料庫。

**理由：** 環境變數是 Docker 容器的宣告式設定，應該隨容器生命週期存在。若寫入資料庫，刪除環境變數後項目仍會殘留，違反直覺。即時合併確保環境變數與 `docker-compose.yml` 保持一致。

**影響層級：** Service 層（`SettingService`）。

### 2. API 回傳區分環境變數項目與資料庫項目

**選擇：** `GET /api/v1/settings` 的 `allowed_directories` 和 `allowed_source_directories` 回傳結構改為物件陣列，每個項目包含 `path` 和 `source`（`"env"` 或 `"db"`）。

**替代方案考量：** 另外用獨立欄位回傳環境變數項目——被否決，因為會讓前端需要合併兩個來源。

**影響層級：** Service 層、Router 層、前端 Schema / Store / Component。

### 3. `ALLOW_WEBUI_SETTING` 在 API 層攔截

**選擇：** 在 `setting` router 的 `update_settings()` 中檢查環境變數，若 `ALLOW_WEBUI_SETTING=false` 且請求包含 `allowed_directories` 或 `allowed_source_directories`，直接回傳 403。

**理由：** 在 router 層攔截最明確，避免深入 service 層的邏輯判斷。前端同時透過 API（`GET /api/v1/settings`）取得 `allow_webui_setting` 旗標來控制 UI 顯示。

**影響層級：** Router 層（`setting.py`）、前端 Component。

### 4. 環境變數格式：逗號分隔

**選擇：** `ALLOWED_DIRECTORIES=/downloads,/media`（逗號分隔）。

**理由：** Docker `environment` 區段不方便傳入 JSON 陣列。逗號分隔是最常見且直覺的格式，與 `PATH` 環境變數慣例一致。

### 5. 前端鎖定項目顯示鎖頭圖示，不可刪除

**選擇：** 來自環境變數的項目在 UI 中顯示鎖頭圖示，隱藏刪除按鈕。`ALLOW_WEBUI_SETTING=false` 時隱藏新增輸入框。

**影響層級：** Component（`SettingView.vue`）。

## Risks / Trade-offs

- **[風險] 環境變數與資料庫項目重複** → 合併時去重，以環境變數為優先（標記為 `"env"`）
- **[風險] 前端快取不同步** → `GET /api/v1/settings` 每次都回傳即時合併結果，不依賴快取
- **[取捨] 回傳結構變更是 breaking change** → `allowed_directories` 和 `allowed_source_directories` 從 `string[]` 變為 `{path, source}[]`，前端需同步更新
