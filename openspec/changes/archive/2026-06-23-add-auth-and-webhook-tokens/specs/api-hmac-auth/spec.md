## ADDED Requirements

### Requirement: HMAC secret 來源與首次啟動自動產生
系統 SHALL 以下列優先順序決定 HMAC secret：(1) 環境變數 `MOVERA_SECRET_KEY`；(2) SQLite 中已持久化的 secret。當兩者皆無時，系統 MUST 於首次啟動自動產生一組高強度隨機 secret 並持久化至 SQLite，以確保重啟後既發 JWT 仍可驗證。系統 MUST NOT 將 secret 回傳前端或寫入回應。

#### Scenario: 使用環境變數設定的 secret
- **WHEN** 啟動時 `MOVERA_SECRET_KEY` 已設定
- **THEN** 系統以該值作為簽章 secret，且不寫入 SQLite

#### Scenario: 首次啟動自動產生 secret
- **WHEN** 啟動時 `MOVERA_SECRET_KEY` 未設定且 SQLite 無已儲存的 secret
- **THEN** 系統產生一組高強度隨機 secret 並持久化至 SQLite

#### Scenario: 重啟後沿用持久化 secret
- **WHEN** 系統重啟且 `MOVERA_SECRET_KEY` 未設定，但 SQLite 已存有 secret
- **THEN** 系統沿用該 secret，先前簽發且未過期的 JWT 仍可通過驗證

### Requirement: API 路由 JWT 簽章驗證
系統 SHALL 對所有 `/api/v1/*` 路由要求合法的 `Authorization: Bearer <jwt>`，但驗證端點 `/api/v1/auth/*`（status / setup / login）除外。後端 MUST 以 HMAC secret 驗證 JWT 的 HS256 簽章與過期時間，驗證失敗一律回傳 401。`/api/v1/auth/*` 與前端靜態資源 MUST NOT 被此驗證攔截。

#### Scenario: 合法 token 通過
- **WHEN** 請求 `/api/v1/*` 並帶有簽章正確且未過期的 JWT
- **THEN** 系統驗證通過並正常處理請求

#### Scenario: 缺少 token
- **WHEN** 請求 `/api/v1/*` 但未帶 `Authorization` 標頭
- **THEN** 系統回傳 401

#### Scenario: 簽章無效
- **WHEN** 請求 `/api/v1/*` 帶有簽章不符或被竄改的 JWT
- **THEN** 系統回傳 401

#### Scenario: token 過期
- **WHEN** 請求 `/api/v1/*` 帶有已過 `exp` 的 JWT
- **THEN** 系統回傳 401

#### Scenario: 登入端點不被攔截
- **WHEN** 未登入使用者請求 `/api/v1/auth/login`（或 `/api/v1/auth/status`、`/api/v1/auth/setup`）
- **THEN** 系統不要求 JWT，正常處理登入流程

### Requirement: 前端附帶 token 與 401 處理
前端 SHALL 對每個 `/api/v1/*` 請求附帶已儲存的 JWT，並在收到 401 時清除 token 並導向登入頁。

#### Scenario: 自動附帶 Authorization 標頭
- **WHEN** 已登入的前端發出 `/api/v1/*` 請求
- **THEN** 請求自動帶上 `Authorization: Bearer <jwt>`

#### Scenario: 401 導向登入
- **WHEN** 前端收到 `/api/v1/*` 回應為 401
- **THEN** 前端清除已儲存的 token 並導向登入頁
