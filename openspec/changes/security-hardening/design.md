## Context

Movera v4.2.0 安全審計揭露多項漏洞，最嚴重的是所有 API 端點無認證保護，加上路徑穿越與 ReDoS 等高風險問題。本設計涵蓋 Critical 至 Medium 級別的修復，以及部分 Low 級別的強化措施。

目前架構：
- **後端**：FastAPI + SQLAlchemy，Layered Architecture（Router → Service → Repository → Model）
- **前端**：Vue 3 + Pinia，透過 `useHttpService` composable 發送 API 請求
- **部署**：Docker 容器，`entrypoint.sh` 已有 gosu 降權機制
- **認證**：完全不存在

## Goals / Non-Goals

**Goals:**
- 修復所有 Critical 和 High 級別漏洞（C-01, H-01~H-05）
- 修復所有 Medium 級別漏洞（M-01~M-08）
- 修復部分 Low 級別漏洞（L-01, L-03, L-04, L-07）
- 維持向下相容性——認證機制預設關閉，透過環境變數啟用

**Non-Goals:**
- 不實作完整的使用者管理系統（帳號/密碼/角色）
- 不實作 OAuth / JWT 認證（過重，不適合此類工具型應用）
- 不處理 L-02（0.0.0.0 綁定是 Docker 部署必要行為）
- 不處理 L-05（GitHub Actions SHA 固定屬 DevOps 範疇，非程式碼修復）
- 不處理 L-06（console.error 清理屬程式碼品質，非安全修復）

## Decisions

### Decision 1: API Key 認證方式——靜態 API Key via 環境變數

**選擇：** 使用環境變數 `MOVERA_API_KEY` 設定單一 API Key，透過 FastAPI Middleware 驗證 `Authorization: Bearer <key>` 或 `X-API-Key: <key>` header。

**替代方案考量：**
- JWT Token：需要使用者管理、token 刷新邏輯，對單一使用者工具型應用過於複雜
- HTTP Basic Auth：每次請求需傳送密碼，且瀏覽器會快取認證資訊
- OAuth 2.0：需要外部 IdP，架構複雜度過高

**理由：** Movera 是單一使用者的自動化工具，API Key 足以阻擋未授權存取。環境變數管理方式與現有 `SQLITE_PATH` 一致。未設定 `MOVERA_API_KEY` 時認證關閉，維持向下相容。

**影響層級：** Middleware（新增） → 所有 Router → 前端 Store/Composable

### Decision 2: 路徑安全——集中式路徑驗證工具函式

**選擇：** 在 `backend/utils/path_security.py` 建立 `validate_path_within(path, allowed_bases)` 和 `sanitize_filename(name)` 工具函式，供 SPA 路由、Webhook worker、Task service、Rename 工具統一呼叫。

**替代方案考量：**
- 各處各自實作驗證邏輯：容易遺漏、不一致
- 使用第三方 path sanitization 套件：增加依賴，且需求簡單不需要

**理由：** 路徑驗證邏輯相同（resolve → is_relative_to），集中管理確保一致性且易於測試。

**影響層級：** Utils（新增）→ main.py（SPA 路由）→ Worker → Service → Utils/rename.py → Utils/move.py

### Decision 3: ReDoS 防護——Python re 模組 timeout 參數

**選擇：** 使用 Python 3.11+ 的 `re.compile(pattern, timeout=...)` 與 `re.sub(pattern, repl, string, timeout=...)` 加入 2 秒超時限制。

**替代方案考量：**
- `google-re2`：需要額外 C 擴充套件，Docker 建置複雜度增加
- 自訂 pattern 複雜度檢查：難以涵蓋所有 ReDoS 模式
- pattern 長度限制：無法阻止短但惡意的 pattern

**理由：** Python 3.13+ 已內建 timeout 支援，無需額外依賴。2 秒對預覽足夠，超時時回傳明確錯誤訊息。

**影響層級：** Service（preview_service.py）→ Utils（rename.py）

### Decision 4: 全域錯誤處理——Exception Middleware

**選擇：** 新增 `@app.exception_handler(Exception)` 全域攔截器，對外回傳 `{"detail": "Internal Server Error"}` 固定訊息，內部以 loguru 記錄完整堆疊。同時修改 `DirectoryNotFound` / `DirectoryAccessDenied` 的錯誤訊息移除路徑資訊。

**影響層級：** backend/backend.py → backend/exceptions/directory_exception.py

### Decision 5: 基礎設施強化——配置檔修正

- `.dockerignore`：新增檔案排除 `.git/`、`.env*`、`node_modules/`、`tests/`、`__pycache__/`、`.vscode/`、`openspec/`
- CORS：將 `allow_methods` 改為 `["GET", "POST", "PUT", "DELETE", "OPTIONS"]`，`allow_headers` 改為 `["Content-Type", "Authorization", "X-API-Key"]`
- Swagger UI：透過 `MOVERA_ENABLE_DOCS` 環境變數控制，預設 `false`
- Trivy CI：`exit-code` 改為 `1`
- Dockerfile：`uv` image 鎖定具體版本 tag
- `alembic.ini`：改用 `%(SQLITE_PATH)s` 環境變數插值（Alembic 內建支援 `%()s` 格式）
- 前端 `useNotification.ts`：移除 `innerHTML` 渲染路徑與 `html` 選項
- Schema 字串欄位加入 `max_length`
- 外部連結加入 `rel="noopener noreferrer"`

**影響層級：** 基礎設施 / 配置 / 前端 Composable / Schema

### Decision 6: Settings API 強化——Pydantic Schema

**選擇：** 新增 `SettingsUpdate` Pydantic schema，取代 `PUT /settings` 的裸 `dict` 參數。僅允許 `allowed_directories: list[str]` 等白名單欄位。

**影響層級：** Schema → Router（setting.py）

## Risks / Trade-offs

- **[Risk] API Key 被洩漏** → Mitigation：API Key 僅透過環境變數注入，不寫入任何設定檔或前端原始碼。Docker 環境透過 `docker-compose.yml` 的 `environment` 或 `.env` 檔傳入。
- **[Risk] 認證機制破壞現有 Webhook 整合** → Mitigation：環境變數未設定時認證關閉；文件說明如何在 BT 下載器腳本中加入 API Key header。
- **[Risk] Regex timeout 可能影響合法的複雜 pattern** → Mitigation：2 秒超時對一般檔名處理充裕；超時時回傳明確的 408/422 錯誤而非靜默失敗。
- **[Risk] `max_length` 限制可能影響現有資料** → Mitigation：選擇寬鬆的限制（name: 255、pattern/path: 1024），遠超合理使用範圍。
- **[Trade-off] API Key 認證安全性有限** → 接受：對單一使用者工具型應用已足夠。未來若需多使用者支援再升級認證機制。
