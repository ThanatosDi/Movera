## Why

目前 Movera 的 `/api/v1/*` 管理 API 與 `/webhook/*` 端點完全沒有任何身分驗證，任何能連到該服務的人都能讀寫任務、修改設定或觸發檔案搬移作業（對應 SECURITY_AUDIT_REPORT 的 SEC01）。本變更導入「管理員登入 + API 請求簽章驗證」與「Webhook 靜態 Bearer Token 管理」兩道分離的防線，讓部署者能在不依賴外部反向代理的情況下保護服務。

## What Changes

- **新增管理員登入機制**：建立登入頁面（使用者名稱 + 密碼），前端以 SHA-256 雜湊密碼後再 POST 至後端，後端加 salt 後存於 SQLite。支援透過 docker compose 環境變數預設帳號密碼，未設定且資料庫無帳號時於首次啟動建立。
- **新增 API HMAC 簽章驗證**：所有 `/api/v1/*` 路由要求合法的 `Authorization: Bearer <jwt>`。登入成功後後端以 HMAC secret 用 HS256 簽發 JWT；後端以同一 secret 驗證簽章。**BREAKING**：未帶合法 token 的 `/api/v1/*` 請求一律回 401。
- **新增 HMAC secret 管理**：secret 可由使用者於 `.env` / docker compose env 設定（`MOVERA_SECRET_KEY`）；未設定時於 container 首次啟動自動產生並持久化（存於 SQLite），確保重啟後 token 仍有效。
- **新增 Webhook Token 管理**：設定頁面可統一管理 webhook token，支援新增、撤銷、命名。Token 以 `movera_` 開頭加雜湊值，存於 SQLite（僅存雜湊，明文僅產生時顯示一次）。
- **Webhook 端點導入 Bearer 驗證（相容模式）**：當 SQLite 無任何有效 token 時 `/webhook/*` 維持放行（不破壞現有下載器腳本）；一旦建立第一個 token，後續請求即要求合法的 `Authorization: Bearer movera_...`。

## Capabilities

### New Capabilities
- `admin-authentication`: 單一管理員帳號的建立、登入、密碼雜湊與儲存、env 預設帳密，以及登入後 JWT 的簽發。
- `api-hmac-auth`: `/api/v1/*` 路由的 JWT(HS256) 簽章驗證、HMAC secret 的 env 設定與首次啟動自動產生持久化。
- `webhook-token-management`: Webhook Bearer token 的新增/撤銷/命名、`movera_` 前綴格式、SQLite 雜湊儲存，以及 `/webhook/*` 的相容式強制驗證。

### Modified Capabilities
<!-- 無既有 spec 的需求變更；本變更僅新增能力。 -->

## Impact

- **後端新增**：`backend/models/`（user、webhook_token、secret 設定）、`backend/repositories/`、`backend/services/`（auth_service、webhook_token_service、secret_service）、`backend/routers/auth.py`、`backend/routers/webhook_token.py`、`backend/middlewares/`（或 FastAPI dependency）做 JWT 與 webhook token 驗證、`backend/utils/`（hashing、jwt、token 產生）。
- **後端修改**：`backend/backend.py`（註冊新 router、套用 API 驗證 dependency）、`backend/routers/webhook.py`（加入相容式 token 驗證）、`backend/dependencies.py`（新增 DI）、`main.py` / `backend/backend.py` lifespan（首次啟動 seed 帳號與 secret）。
- **資料庫**：新增 Alembic migration（`user`、`webhook_token` 資料表；secret 可沿用 `setting` 表）。
- **前端新增**：登入頁 View、auth store（存 JWT、注入 Authorization header）、webhook token 管理 UI（設定頁區塊）、路由守衛（未登入導向登入頁）。
- **前端修改**：API 請求層統一附帶 `Authorization: Bearer <jwt>`、401 時導向登入；`src/routers/index.ts`、`src/stores/`、`SettingView.vue`。
- **設定 / 文件**：`.env.example`、README 環境變數表（`MOVERA_SECRET_KEY`、`MOVERA_ADMIN_USERNAME`、`MOVERA_ADMIN_PASSWORD`）、downloader 腳本需更新以帶 webhook token 的遷移說明。
- **相依套件**：後端需新增 JWT（如 `pyjwt`）與密碼雜湊（`passlib`/`bcrypt` 或標準庫 `hashlib`）相關套件。
