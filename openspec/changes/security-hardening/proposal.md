## Why

安全審計（SECURITY_AUDIT_REPORT.md）揭露 Movera v4.2.0 存在 1 項 Critical、5 項 High、8 項 Medium 級別的安全漏洞。最關鍵的問題包括：所有 API 端點無認證保護、SPA 路由可被路徑穿越攻擊讀取任意檔案、Webhook 與任務的檔案路徑未經驗證可導致任意檔案操作，以及使用者自定義 Regex 可觸發 ReDoS 阻斷服務。這些漏洞使得任何能連線到伺服器的攻擊者皆可完全操控系統，必須立即修復。

## What Changes

### P0 — Critical / High（必須修復）
- 新增 API Key 認證中介層，保護所有 `/api/v1/*` 及 `/webhook/*` 端點（C-01）
- 修復 SPA catch-all 路由路徑穿越漏洞，加入 `resolve()` + `is_relative_to()` 檢查（H-01）
- Webhook `filepath` 加入路徑白名單驗證（H-02）
- Task `move_to` 建立/更新時驗證路徑位於 `allowed_directories` 白名單內（H-03）
- Regex 編譯與執行加入超時限制，防止 ReDoS 攻擊（H-04）
- 建立 `.dockerignore` 檔案，排除敏感檔案進入映像檔（H-05）

### P1 — Medium（應修復）
- Rename 產出的檔名加入路徑穿越防護，拒絕含 `../` 或絕對路徑的結果（M-01）
- `PUT /settings` 改用明確 Pydantic schema 取代裸 `dict`（M-02）
- 錯誤訊息移除內部路徑資訊，僅回傳通用訊息（M-03）
- 新增全域 Exception Handler 攔截未預期的 500 錯誤（M-04）
- CORS 收緊 `allow_methods` 和 `allow_headers` 為明確白名單（M-05）
- 透過環境變數控制 Swagger UI / ReDoc，正式環境預設關閉（M-06）
- 移除前端通知系統的 `innerHTML` 渲染路徑（M-07）
- Trivy 掃描改為 `exit-code: 1` 以阻擋高危漏洞部署（M-08）

### P2 — Low（建議修復）
- Schema 字串欄位加入 `max_length` 限制（L-01）
- `alembic.ini` 改用環境變數讀取資料庫路徑（L-03）
- Dockerfile 中 `uv` 鎖定特定版本（L-04）
- 外部連結加入 `rel="noopener noreferrer"`（L-07）

## Capabilities

### New Capabilities
- `api-key-auth`: API Key 認證機制——中介層驗證、設定管理、前端 header 注入
- `path-security`: 路徑安全防護——SPA 路徑穿越修復、Webhook/move_to/rename 路徑驗證與消毒
- `regex-safety`: Regex 安全執行——超時限制、長度/複雜度檢查、ReDoS 防護
- `error-handling-hardening`: 錯誤處理強化——全域 500 攔截器、錯誤訊息消毒、移除內部路徑洩漏

### Modified Capabilities
（無現有 spec 層級的需求變更）

## Impact

- **後端 API**：所有路由需通過認證中介層；路徑相關操作需加入驗證邏輯；Regex 相關服務需加入超時機制
- **前端**：API 呼叫需附帶 API Key header；移除 `innerHTML` 渲染路徑；通知系統 schema 調整
- **基礎設施**：新增 `.dockerignore`；調整 Dockerfile、CI workflow、CORS 配置
- **Schema/Validation**：`backend/schemas.py` 多處欄位需加入 `max_length`；新增 `SettingsUpdate` schema
- **Dependencies**：無新增外部依賴（使用 Python 3.13 內建 `re` timeout 功能）
- **Breaking Changes**：無（API Key 認證可透過環境變數 opt-in，預設關閉以維持向下相容）
