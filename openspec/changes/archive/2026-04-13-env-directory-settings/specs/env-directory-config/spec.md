## ADDED Requirements

### Requirement: 系統 SHALL 支援透過環境變數設定目錄白名單

系統 SHALL 支援以下環境變數，用於預先配置目錄白名單：
- `ALLOWED_DIRECTORIES`：逗號分隔的絕對路徑清單
- `ALLOWED_SOURCE_DIRECTORIES`：逗號分隔的絕對路徑清單

環境變數中的路徑 SHALL 在 `GET /api/v1/settings` 時與資料庫設定合併回傳，且不寫入資料庫。

#### Scenario: 透過環境變數注入 allowed_directories
- **WHEN** 環境變數設定為 `ALLOWED_DIRECTORIES=/downloads,/media`
- **THEN** `GET /api/v1/settings` 的 `allowed_directories` SHALL 包含 `{"path": "/downloads", "source": "env"}` 和 `{"path": "/media", "source": "env"}`

#### Scenario: 環境變數與資料庫項目合併
- **WHEN** 環境變數設定為 `ALLOWED_DIRECTORIES=/downloads`，且資料庫中已有 `/media`
- **THEN** `GET /api/v1/settings` 的 `allowed_directories` SHALL 包含 `{"path": "/downloads", "source": "env"}` 和 `{"path": "/media", "source": "db"}`

#### Scenario: 環境變數與資料庫項目重複時去重
- **WHEN** 環境變數設定為 `ALLOWED_DIRECTORIES=/downloads`，且資料庫中也有 `/downloads`
- **THEN** `GET /api/v1/settings` 的 `allowed_directories` SHALL 僅包含一筆 `{"path": "/downloads", "source": "env"}`（環境變數優先）

#### Scenario: 環境變數未設定時維持現有行為
- **WHEN** `ALLOWED_DIRECTORIES` 環境變數未設定或為空字串
- **THEN** `allowed_directories` SHALL 僅回傳資料庫中的項目，每項標記為 `{"source": "db"}`

#### Scenario: 環境變數中的無效路徑被忽略
- **WHEN** 環境變數設定為 `ALLOWED_DIRECTORIES=/downloads,relative/path,/media`
- **THEN** 系統 SHALL 忽略 `relative/path`，僅包含 `/downloads` 和 `/media`

---

### Requirement: 環境變數項目 SHALL 不可被刪除

透過環境變數注入的路徑項目 SHALL 在 `PUT /api/v1/settings` 時受到保護，不可被移除。

#### Scenario: 嘗試刪除環境變數項目
- **WHEN** 環境變數設定了 `/downloads`，使用者透過 API 傳入的 `allowed_directories` 不包含 `/downloads`
- **THEN** 系統 SHALL 自動保留 `/downloads`（環境變數項目不受 API 更新影響）

#### Scenario: 資料庫項目可正常刪除
- **WHEN** `/media` 僅存在於資料庫中（非環境變數），使用者透過 API 傳入的 `allowed_directories` 不包含 `/media`
- **THEN** 系統 SHALL 從資料庫中移除 `/media`

---

### Requirement: `ALLOW_WEBUI_SETTING` SHALL 控制前端目錄設定能力

系統 SHALL 支援環境變數 `ALLOW_WEBUI_SETTING`（預設 `true`）。當設為 `false` 時，系統 SHALL 禁止透過 Web UI 和 API 新增或修改 `allowed_directories` 和 `allowed_source_directories`。

#### Scenario: ALLOW_WEBUI_SETTING=true 時正常操作
- **WHEN** `ALLOW_WEBUI_SETTING=true` 或未設定
- **THEN** 前端 SHALL 顯示新增輸入框，`PUT /api/v1/settings` SHALL 正常處理 `allowed_directories` 和 `allowed_source_directories` 更新

#### Scenario: ALLOW_WEBUI_SETTING=false 時 API 拒絕修改
- **WHEN** `ALLOW_WEBUI_SETTING=false`，且 `PUT /api/v1/settings` 請求包含 `allowed_directories` 或 `allowed_source_directories`
- **THEN** API SHALL 回傳 403 Forbidden，並附帶訊息說明目錄設定已被管理者鎖定

#### Scenario: ALLOW_WEBUI_SETTING=false 時前端隱藏新增功能
- **WHEN** `ALLOW_WEBUI_SETTING=false`
- **THEN** 前端 SHALL 隱藏 `allowed_directories` 和 `allowed_source_directories` 的新增輸入框，僅顯示現有清單（唯讀）

#### Scenario: GET API 回傳 allow_webui_setting 旗標
- **WHEN** 前端請求 `GET /api/v1/settings`
- **THEN** 回應 SHALL 包含 `allow_webui_setting` 布林值欄位，反映目前的環境變數設定

---

### Requirement: 前端 SHALL 區分環境變數與資料庫項目

設定頁面 SHALL 在目錄列表中明確區分來自環境變數和來自資料庫的項目。

#### Scenario: 環境變數項目顯示鎖定標示
- **WHEN** 某個路徑項目的 `source` 為 `"env"`
- **THEN** UI SHALL 顯示鎖頭圖示，且不顯示刪除按鈕

#### Scenario: 資料庫項目顯示刪除按鈕
- **WHEN** 某個路徑項目的 `source` 為 `"db"` 且 `ALLOW_WEBUI_SETTING` 不為 `false`
- **THEN** UI SHALL 顯示刪除按鈕，允許使用者移除該項目
