## 1. 前置準備

- [x] 1.1 新增後端相依套件：`pyjwt`（JWT HS256）至 `pyproject.toml`，執行 `uv sync`
- [x] 1.2 建立資料模型骨架：`backend/models/user.py`（`username` PK、`password_hash`、`salt`、`created_at`）與 `backend/models/webhook_token.py`（`id`、`name`、`token_hash`、`created_at`、`revoked_at`），並於 `backend/models/__init__.py` 匯出
- [x] 1.3 建立 Alembic migration 新增 `user`、`webhook_token` 資料表（secret 沿用既有 `setting` 表）
- [x] 1.4 建立工具模組骨架：`backend/utils/security.py`（salted SHA-256 雜湊、`secrets.token_urlsafe` 產生器）與 `backend/utils/jwt.py`（簽發／驗證 JWT）
- [x] 1.5 於 `backend/utils/env_config.py` 新增讀取 `MOVERA_SECRET_KEY`、`MOVERA_ADMIN_USERNAME`、`MOVERA_ADMIN_PASSWORD` 的函式

## 2. HMAC secret 管理

### 2.1 🔴 紅燈 - 撰寫 secret 解析測試
- [x] 設定 `MOVERA_SECRET_KEY` 時回傳該值且不寫入 DB
- [x] 無 env 且 DB 無 secret 時自動產生並持久化至 `setting` 表
- [x] 重啟（無 env、DB 有 secret）時沿用既有 secret
- [x] 執行測試，確認全部失敗

### 2.2 🟢 綠燈 - 實作 secret 解析功能
- [x] 實作 `SecretService`（或併入 `AuthService`）依 env → DB → 自動產生 的優先序解析 secret
- [x] 於應用啟動流程（lifespan，migration 之後）初始化 secret
- [x] 執行測試，確認全部通過

### 2.3 🔵 重構 - 優化 secret 程式碼
- [x] 抽離 secret 取得邏輯為單一可注入來源，避免重複讀取
- [x] 執行測試，確認仍然通過

## 3. 管理員帳號與登入

### 3.1 🔴 紅燈 - 撰寫帳號與登入測試
- [x] 建立帳號時以 `sha256(salt + 收到的 sha256 值)` 儲存，DB 無明文
- [x] env 預設帳密且 DB 無帳號時於啟動建立帳號；已有帳號時不覆寫
- [x] `POST /auth/login` 帳密正確回傳含 `sub`/`exp` 的 HS256 JWT
- [x] 帳密錯誤回傳 401 且不發放 token
- [x] 執行測試，確認全部失敗

### 3.2 🟢 綠燈 - 實作帳號與登入功能
- [x] 實作 `UserRepository` 與 `AuthService`（建立帳號、驗證密碼、簽發 JWT）
- [x] 實作 `backend/routers/auth.py` 的 `POST /auth/login`
- [x] 於 `backend/dependencies.py` 新增對應 DI
- [x] 於啟動流程加入 env 帳號 seed 邏輯
- [x] 執行測試，確認全部通過

### 3.3 🔵 重構 - 優化帳號與登入程式碼
- [x] 統一密碼雜湊與 JWT 工具的呼叫介面
- [x] 執行測試，確認仍然通過

## 4. API 路由 JWT 驗證

### 4.1 🔴 紅燈 - 撰寫 API 驗證測試
- [x] 帶合法 JWT 的 `/api/v1/*` 請求通過
- [x] 缺少／簽章無效／過期 token 的 `/api/v1/*` 請求回 401
- [x] `/auth/login` 與 SPA 靜態路由不被攔截
- [x] 執行測試，確認全部失敗

### 4.2 🟢 綠燈 - 實作 API 驗證功能
- [x] 實作 `require_jwt` FastAPI dependency（驗證 HS256 簽章與 `exp`）
- [x] 於 `backend/backend.py` 將驗證 dependency 套用至所有 `/api/v1/*` router
- [x] 確認 `/auth/login`、webhook、靜態資源排除於驗證之外
- [x] 執行測試，確認全部通過

### 4.3 🔵 重構 - 優化 API 驗證程式碼
- [x] 整理受保護 router 的註冊方式，集中驗證設定
- [x] 執行測試，確認仍然通過

## 5. Webhook token 管理

### 5.1 🔴 紅燈 - 撰寫 token 管理測試
- [x] 產生 token 回傳 `movera_<隨機>` 明文一次，DB 僅存 `sha256(token)`
- [x] 列出 token 僅顯示名稱／時間／狀態，不顯示明文
- [x] 撤銷 token 後標記 `revoked_at`
- [x] 建立時可設定名稱
- [x] 執行測試，確認全部失敗

### 5.2 🟢 綠燈 - 實作 token 管理功能
- [x] 實作 `WebhookTokenRepository` 與 `WebhookTokenService`（產生／列出／撤銷／命名）
- [x] 實作 `backend/routers/webhook_token.py`（受 `require_jwt` 保護的 CRUD 端點）
- [x] 於 `dependencies.py` 與 `backend.py` 註冊
- [x] 執行測試，確認全部通過

### 5.3 🔵 重構 - 優化 token 管理程式碼
- [x] 抽離 token 產生／雜湊比對的共用邏輯
- [x] 執行測試，確認仍然通過

## 6. Webhook 相容式驗證

### 6.1 🔴 紅燈 - 撰寫 webhook 驗證測試
- [x] DB 無有效 token 時 `/webhook/*` 放行
- [x] 存在有效 token 時，帶合法 `Bearer movera_...` 通過
- [x] 存在有效 token 但未帶／帶已撤銷／不存在 token 時回 401
- [x] 執行測試，確認全部失敗

### 6.2 🟢 綠燈 - 實作 webhook 驗證功能
- [x] 實作 `require_webhook_token` dependency（相容式邏輯）
- [x] 套用至 `backend/routers/webhook.py` 的 `/webhook/*` 端點
- [x] 執行測試，確認全部通過

### 6.3 🔵 重構 - 優化 webhook 驗證程式碼
- [x] 共用 token 比對邏輯與管理服務，避免重複
- [x] 執行測試，確認仍然通過

## 7. 前端登入與守衛

### 7.1 🔴 紅燈 - 撰寫登入前端測試
- [x] auth store：login 成功儲存 token、logout 清除 token
- [x] 密碼於送出前以 SHA-256 雜湊，payload 不含明文
- [x] 路由守衛：未登入存取受保護頁導向登入頁
- [x] API 層收到 401 時清 token 並導向登入
- [x] 執行測試（Vitest），確認全部失敗

### 7.2 🟢 綠燈 - 實作登入前端功能
- [x] 建立 `LoginView`（使用者名稱、密碼欄位、前端 SHA-256）
- [x] 建立 `authStore`（Pinia）管理 token 與登入狀態
- [x] 於 API/composable 層注入 `Authorization: Bearer` 與 401 攔截
- [x] 於 `src/routers/index.ts` 加入全域守衛與登入路由，新增 i18n 字串
- [x] 執行測試，確認全部通過

### 7.3 🔵 重構 - 優化登入前端程式碼
- [x] 抽離 token 儲存與 header 注入為可重用 composable
- [x] 執行測試，確認仍然通過

## 8. 前端 Webhook token 管理 UI

### 8.1 🔴 紅燈 - 撰寫 token 管理 UI 測試
- [x] 列表顯示 token 名稱／狀態
- [x] 新增 token 後一次性顯示明文
- [x] 撤銷 token 後列表狀態更新
- [x] 執行測試，確認全部失敗

### 8.2 🟢 綠燈 - 實作 token 管理 UI
- [x] 於 `SettingView.vue` 新增 webhook token 管理區塊（列表／新增／一次性明文／撤銷）
- [x] 串接對應 API 與 store
- [x] 執行測試，確認全部通過

### 8.3 🔵 重構 - 優化 token 管理 UI
- [x] 抽離可重用元件與表單邏輯
- [x] 執行測試，確認仍然通過

## 9. 整合測試
- [x] 9.1 後端：完整登入 → 取得 JWT → 存取 `/api/v1/*` → 管理 webhook token → webhook 驗證 的端到端 pytest
- [ ] 9.2 前端：以 MCP Chrome DevTools 驗證登入流程、未登入導向、token 管理 UI（導航／填表／截圖／檢查 network 401）
- [x] 9.3 驗證首次啟動情境：無 env 自動產生 secret、env 預設帳號建立

## 10. 文件更新
- [x] 10.1 更新 `.env.example`：新增 `MOVERA_SECRET_KEY`、`MOVERA_ADMIN_USERNAME`、`MOVERA_ADMIN_PASSWORD`
- [x] 10.2 更新 `README.md`：環境變數表、登入與 API 認證說明、webhook token 啟用後各下載器腳本加上 `Authorization: Bearer movera_...` 的遷移說明
- [x] 10.3 補充安全建議（建議部署於 HTTPS／反向代理後）

## 11. 程式碼品質檢查
- [x] 11.1 後端 `ruff` 檢查通過、`uv run pytest tests/backend/ -v` 全綠
- [x] 11.2 前端 `npm run build`（型別檢查）與 `npm run test:run` 全綠
- [x] 11.3 確認無明文密碼／secret／token 寫入日誌或回應
