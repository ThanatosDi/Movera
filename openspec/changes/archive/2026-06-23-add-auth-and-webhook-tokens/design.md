## Context

Movera 目前所有 `/api/v1/*` 與 `/webhook/*` 端點皆無身分驗證（SEC01）。後端為分層架構（Router → Service → Repository → Model），設定以 key/value 存於 `setting` 表，DI 集中於 `backend/dependencies.py`，app 組裝與 router 註冊在 `backend/backend.py`，DB migration 由 Alembic 在 lifespan 啟動時自動 `upgrade head`。前端為 Vue 3 + Pinia SPA，由 `main.py` 提供靜態檔案與 SPA fallback。

本設計需在「不依賴外部反向代理」的前提下，為管理 API 與 webhook 各自建立一道驗證機制，且不破壞既有下載器整合。

## Goals / Non-Goals

**Goals:**
- `/api/v1/*` 全面要求合法 JWT（HS256，以 HMAC secret 簽章/驗章）。
- 提供管理員登入頁與單一帳號機制；密碼前端 SHA-256、後端加 salt 後存 SQLite。
- HMAC secret 可由 env 設定，未設定則首次啟動自動產生並持久化。
- Webhook 提供靜態 Bearer token 管理（新增/撤銷/命名），`movera_` 前綴，SQLite 僅存雜湊。
- Webhook 相容模式：無 token 放行，有 token 即強制。

**Non-Goals:**
- 多使用者、角色權限（RBAC）、密碼重設信箱流程。
- TLS 終結（仍建議由反向代理或部署者處理 HTTPS）。
- JWT refresh token / 黑名單撤銷機制（採短/中效期 + 重新登入）。
- OAuth / 第三方登入。

## Decisions

### D1：API 驗證採 JWT(HS256)，以 HMAC secret 簽章
- **選擇**：登入成功後，後端用 `MOVERA_SECRET_KEY` 以 HS256 簽發 JWT（claims：`sub=username`、`iat`、`exp`）。前端存於 Pinia/localStorage，每次 `/api/v1/*` 請求帶 `Authorization: Bearer <jwt>`。後端 FastAPI dependency 驗證簽章與 `exp`。
- **理由**：統一了需求中的「HMAC secret」（點1）與「登入後產生簽章」（點3）——JWT 的 HS256 簽章本身就是 HMAC。比「前端持金鑰逐請求簽章」簡單、不需把 secret 暴露給 JS、與標準工具相容。
- **替代方案**：前端持 per-session 金鑰對 method+path+body+timestamp 逐請求算 HMAC——較複雜、金鑰外洩風險高、需處理時鐘偏移，已排除。
- **影響層級**：Router（新增 `auth.py`）、Service（`auth_service`）、Utils（`jwt` 工具）、`backend.py`（套用驗證 dependency 至 `/api/v1` router 群）。
- **套件**：`pyjwt`。

### D2：API 驗證以全域 dependency 套用於 `/api/v1/*`
- **選擇**：以 FastAPI `dependencies=[Depends(require_jwt)]` 套用在受保護 router（逐 router 套用，而非整個 `/api/v1` 前綴）。驗證 router 位於 `/api/v1/auth/*` 但**不**套用守衛，因此維持公開；SPA 靜態路由、webhook 亦不套用。
- **路徑注意**：auth 端點刻意置於 `/api/v1/auth/*`（而非 `/auth/*`），以重用既有 Vite dev proxy 與 PWA service worker 對 `/api` 的轉發與 NetworkOnly 規則，避免開發模式下被 SPA fallback 攔截。
- **理由**：集中、不需逐 endpoint 標註；避免遺漏。
- **替代方案**：自訂 ASGI middleware 攔截路徑前綴——較難回傳結構化 401 與整合 OpenAPI，排除。
- **影響層級**：`backend.py`、`dependencies.py`。

### D3：HMAC secret 來源與首次啟動自動產生
- **選擇**：啟動時依序解析——(1) 環境變數 `MOVERA_SECRET_KEY` 若有則用之；(2) 否則查 SQLite `setting` 表 key=`secret_key`；(3) 皆無則 `secrets.token_urlsafe(48)` 產生並寫入 `setting` 表持久化。secret 永不回傳前端。
- **理由**：滿足點1（env 可設定、未設定則首次啟動自動產生）；存 `setting` 表可重啟後維持 JWT 有效，沿用既有資料表減少 migration。
- **權衡**：env 設定的 secret 不寫入 DB（避免雙來源衝突），每次啟動以 env 為準。
- **影響層級**：`secret_service`（或併入 `auth_service`）、lifespan/啟動流程、`setting` repository。

### D4：單一管理員帳號、env 預設、密碼雜湊
- **選擇**：新增 `user` 表（`username` PK、`password_hash`、`salt`、`created_at`）。前端送 `sha256(password)`；後端再 `sha256(salt + received)` 後存（salt 每帳號隨機）。啟動 seed：若 env 提供 `MOVERA_ADMIN_USERNAME` / `MOVERA_ADMIN_PASSWORD` 且 DB 無帳號則建立（env 的密碼後端自行 sha256 處理對齊前端格式）。
- **理由**：對齊使用者選擇（前端 SHA-256 為最終值，後端加 salt 儲存）。salt 防彩虹表 / 防 DB 外洩時直接比對。
- **權衡**：SHA-256 為快速雜湊，抗暴力破解弱於 bcrypt；已依使用者決定採用，並以 salt + 建議 HTTPS 緩解。記錄於 Risks。
- **影響層級**：Model（`user`）、Repository、Service（`auth_service`）、Router（`auth.py`）、migration、lifespan seed。

### D5：Webhook token 管理與相容式強制
- **選擇**：新增 `webhook_token` 表（`id`、`name`、`token_hash`、`prefix`、`created_at`、`revoked_at`）。產生時回傳明文 `movera_<隨機>` 僅顯示一次，DB 僅存 `sha256(token)`。驗證時取請求 Bearer 算 sha256 比對未撤銷的 token。`/webhook/*` 依賴 `require_webhook_token`：DB 無「有效（未撤銷）token」→ 放行；存在任一有效 token → 要求合法 Bearer，否則 401。
- **理由**：滿足點4（統一管理、新增/撤銷/命名、`movera_` 前綴、SQLite 儲存）與相容模式（不破壞既有腳本）。
- **替代方案**：webhook 共用 API 的 JWT——但 webhook 來自下載器無法登入，需獨立靜態 token，故分離。
- **影響層級**：Model（`webhook_token`）、Repository、Service、Router（`webhook_token.py` 管理 + `webhook.py` 加驗證 dependency）、migration、前端設定頁 UI。

### D6：前端整合
- **選擇**：新增 `LoginView` 與 auth store（存 token、login/logout、注入 `Authorization` header）；API 層攔截 401 → 清 token 並導向登入；Vue Router 全域守衛保護需登入頁面。設定頁新增 webhook token 管理區塊（列表、新增＋一次性顯示明文、撤銷）。
- **影響層級**：Views（`LoginView`）、Stores（`authStore`）、Router（`src/routers/index.ts` 守衛）、API/composable 層、`SettingView.vue`、i18n locales。

## Risks / Trade-offs

- **SHA-256 而非慢雜湊（bcrypt/argon2）** → salt + 強烈建議部署於 HTTPS / 反向代理後；於 README 標註安全建議。日後可在不變更前端契約下，將後端儲存升級為 bcrypt(received)。
- **JWT 無主動撤銷機制** → 採中短效期（如 12h）+ 重新登入；secret 變更（重設 env 或清除 `setting`）會使所有既發 token 失效，作為緊急撤銷手段。
- **首次啟動 race（migration 未完成即讀 secret）** → secret 初始化置於 Alembic `upgrade head` 之後（lifespan 內）。
- **Webhook 相容模式的空窗** → 在「建立第一個 token 前」webhook 仍開放；於 UI/README 明確提示「建立 token 即啟用強制驗證，並需同步更新下載器腳本」。
- **既有部署升級** → 首次帶 auth 啟動後，未登入的前端會被導向登入頁；README 需說明預設帳密的設定方式與升級步驟。
- **secret 同時存在 env 與 DB** → 規則固定為 env 優先，避免歧義（D3）。

## Migration Plan

1. 新增 Alembic migration 建立 `user`、`webhook_token` 表（`setting` 表沿用存 secret）。
2. 部署時建議於 docker compose env 設定 `MOVERA_SECRET_KEY`、`MOVERA_ADMIN_USERNAME`、`MOVERA_ADMIN_PASSWORD`；未設定則首次啟動自動產生 secret，並需手動建立帳號（或提供首次設定流程）。
3. 既有 webhook 下載器腳本：在建立第一個 webhook token 前不受影響；啟用 token 後更新各腳本加上 `Authorization: Bearer movera_...`（README 補充各下載器設定範例）。
4. **Rollback**：移除 API 驗證 dependency 即可恢復開放；migration 可 `downgrade` 移除新表（資料遺失可接受，僅含帳號與 token）。

## Open Questions

- 首次無 env 帳密時，是否提供「首次啟動設定精靈」頁面建立帳號，或要求必須以 env 設定？（建議：允許無帳號時前端顯示「初始化設定」頁建立第一組帳密，再導向登入。）
- JWT 有效期長度與是否需要「記住我」延長期。（建議預設 12h。）
