## ADDED Requirements

### Requirement: Webhook token 產生與儲存
系統 SHALL 允許管理員產生 webhook token。Token MUST 以 `movera_` 為前綴後接高強度隨機雜湊值。SQLite MUST 僅儲存 token 的雜湊（如 SHA-256）與名稱、建立時間、撤銷狀態，明文 token MUST 僅於產生當下回傳一次，不再次提供。

#### Scenario: 產生新 token
- **WHEN** 管理員在設定頁建立新 token 並指定名稱
- **THEN** 系統產生 `movera_<隨機值>` 格式的 token，回傳明文一次，並於 SQLite 僅儲存其雜湊與名稱

#### Scenario: 明文僅顯示一次
- **WHEN** 管理員在建立後再次檢視 token 列表
- **THEN** 系統僅顯示名稱、前綴與遮蔽後的識別資訊，不再顯示完整明文 token

### Requirement: Webhook token 管理
系統 SHALL 提供統一的設定頁面區塊，供管理員列出、新增、命名與撤銷 webhook token。被撤銷的 token MUST 立即失效。

#### Scenario: 列出 token
- **WHEN** 管理員開啟設定頁的 webhook token 區塊
- **THEN** 系統列出所有 token 的名稱、建立時間與狀態（有效／已撤銷）

#### Scenario: 撤銷 token
- **WHEN** 管理員撤銷某個 token
- **THEN** 系統將該 token 標記為已撤銷，後續以該 token 的 webhook 請求一律被拒

#### Scenario: 設定 token 名稱
- **WHEN** 管理員建立 token 時提供名稱
- **THEN** 系統儲存該名稱並於列表顯示，用以識別用途

### Requirement: Webhook 端點相容式 Bearer 驗證
系統 SHALL 對 `/webhook/*` 端點採相容式驗證：當 SQLite 中不存在任何有效（未撤銷）token 時 MUST 放行請求；一旦存在任一有效 token，則 MUST 要求合法的 `Authorization: Bearer movera_...`，否則回傳 401。

#### Scenario: 尚無 token 時放行
- **WHEN** SQLite 中沒有任何有效 token，且收到 `/webhook/*` 請求
- **THEN** 系統正常處理請求，不要求 Authorization 標頭

#### Scenario: 有 token 後要求驗證
- **WHEN** SQLite 中已存在至少一個有效 token，且 `/webhook/*` 請求帶有合法的 `Authorization: Bearer movera_...`
- **THEN** 系統驗證通過並正常處理請求

#### Scenario: 有 token 但未帶或帶無效 token
- **WHEN** SQLite 中已存在至少一個有效 token，但 `/webhook/*` 請求未帶 token 或帶已撤銷／不存在的 token
- **THEN** 系統回傳 401

#### Scenario: 撤銷後該 token 失效
- **WHEN** 某 token 已被撤銷，且 `/webhook/*` 請求使用該 token
- **THEN** 系統回傳 401
