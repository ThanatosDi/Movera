## ADDED Requirements

### Requirement: API Key 認證中介層
系統 SHALL 提供 API Key 認證機制。當環境變數 `MOVERA_API_KEY` 已設定且非空時，所有 `/api/v1/*` 及 `/webhook/*` 端點 SHALL 要求請求包含有效的 API Key。API Key SHALL 支援透過 `Authorization: Bearer <key>` header 或 `X-API-Key: <key>` header 傳遞。

#### Scenario: 認證啟用且 API Key 正確
- **WHEN** `MOVERA_API_KEY` 環境變數已設定，且請求包含正確的 `Authorization: Bearer <key>` header
- **THEN** 請求 SHALL 正常通過認證並由對應的路由處理

#### Scenario: 認證啟用且使用 X-API-Key header
- **WHEN** `MOVERA_API_KEY` 環境變數已設定，且請求包含正確的 `X-API-Key: <key>` header
- **THEN** 請求 SHALL 正常通過認證並由對應的路由處理

#### Scenario: 認證啟用但缺少 API Key
- **WHEN** `MOVERA_API_KEY` 環境變數已設定，且請求未包含任何認證 header
- **THEN** 系統 SHALL 回傳 HTTP 401 Unauthorized，body 為 `{"detail": "Unauthorized"}`

#### Scenario: 認證啟用但 API Key 錯誤
- **WHEN** `MOVERA_API_KEY` 環境變數已設定，且請求包含的 API Key 與環境變數不符
- **THEN** 系統 SHALL 回傳 HTTP 401 Unauthorized，body 為 `{"detail": "Unauthorized"}`

#### Scenario: 認證未啟用時所有請求通過
- **WHEN** `MOVERA_API_KEY` 環境變數未設定或為空字串
- **THEN** 所有請求 SHALL 不經認證直接通過（向下相容模式）

### Requirement: 靜態資源不受認證保護
SPA 靜態資源路由（`/`、`/assets/*`、`/{full_path:path}` fallback）SHALL 不受 API Key 認證保護，確保前端頁面可正常載入。

#### Scenario: 靜態資源不需認證
- **WHEN** 使用者存取 `/` 或 `/assets/index.js` 等靜態資源路徑
- **THEN** 系統 SHALL 不檢查 API Key，直接回傳靜態檔案

### Requirement: 前端 API 請求附帶 API Key
前端 `useHttpService` composable SHALL 在每個 API 請求的 header 中附帶 API Key。API Key SHALL 從應用程式設定或環境變數中讀取。

#### Scenario: 前端請求自動附帶 API Key header
- **WHEN** 前端透過 `useHttpService` 發送任何 API 請求
- **THEN** 請求 SHALL 自動包含 `X-API-Key` header

### Requirement: Swagger UI 依環境變數控制顯示
系統 SHALL 透過環境變數 `MOVERA_ENABLE_DOCS` 控制 Swagger UI 與 ReDoc 的顯示。當該變數為 `true` 時啟用 `/docs` 與 `/redoc`，否則 SHALL 設定 `docs_url=None`、`redoc_url=None`、`openapi_url=None`。

#### Scenario: 文件端點預設關閉
- **WHEN** `MOVERA_ENABLE_DOCS` 環境變數未設定或不為 `true`
- **THEN** 存取 `/docs`、`/redoc`、`/openapi.json` SHALL 回傳 404

#### Scenario: 文件端點啟用
- **WHEN** `MOVERA_ENABLE_DOCS` 環境變數設定為 `true`
- **THEN** `/docs`、`/redoc`、`/openapi.json` SHALL 正常運作
