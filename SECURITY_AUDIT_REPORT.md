# Movera v4.2.0 Security Audit Report

**Date:** 2026-04-12
**Branch:** `feat/v4.2.0`
**Auditor:** Claude Code (Automated Static Analysis)
**Scope:** Full-stack application — Python/FastAPI backend, Vue.js/TypeScript frontend, Docker/CI infrastructure

---

## Executive Summary

本次針對 Movera v4.2.0 進行全面靜態安全審計，涵蓋後端 API、前端 UI、基礎設施與 CI/CD 配置。共發現 **27 項安全發現**，其中包含 **1 項 Critical**、**5 項 High**、**8 項 Medium**、**7 項 Low** 及 **6 項 Info** 級別的項目。

最關鍵的風險為：**整個 API 無任何認證機制**、**SPA 路由存在路徑穿越漏洞（任意檔案讀取）**、以及 **Webhook 端點接受未驗證的檔案路徑導致任意檔案操作**。

| Severity | Count |
|----------|-------|
| Critical | 1 |
| High     | 5 |
| Medium   | 8 |
| Low      | 7 |
| Info     | 6 |

---

## Critical

### C-01: 所有 API 端點無任何認證與授權機制

| 項目 | 內容 |
|------|------|
| **Severity** | Critical |
| **Files** | `backend/routers/*.py`, `backend/dependencies.py` |
| **Category** | Authentication / Authorization |

**Description:**
整個應用程式不存在任何形式的認證（Authentication）或授權（Authorization）機制。所有路由（task、tag、preset_rule、setting、log、preview、webhook、directory）皆為公開存取，無 API Key、JWT、OAuth 或 Basic Auth 保護。

**Impact:**
- 任何能連線到伺服器的攻擊者可：建立/刪除任務、修改系統設定（包括 `allowed_directories`）、瀏覽伺服器檔案系統、觸發檔案搬移/重新命名操作。
- Webhook 端點 `/webhook/qbittorrent/on-complete` 接受任意 POST 請求並觸發背景檔案操作。

**Recommendation:**
- 至少在所有 `/api/v1/*` 及 `/webhook/*` 路由加入 API Key 或 Bearer Token 認證中介層。
- 考慮依角色區分讀取與寫入權限。

---

## High

### H-01: SPA Catch-all 路由存在路徑穿越漏洞（任意檔案讀取）

| 項目 | 內容 |
|------|------|
| **Severity** | High |
| **File** | `main.py:25-33` |
| **Category** | Path Traversal |

**Description:**
```python
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    file_path = DIST_DIR / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
```

`full_path` 未經過路徑正規化或穿越檢查。攻擊者可透過 `GET /../../etc/passwd` 類型的請求讀取伺服器上任意檔案。程式碼未驗證解析後的路徑仍在 `DIST_DIR` 之下。

**Recommendation:**
```python
resolved = (DIST_DIR / full_path).resolve()
if resolved.is_relative_to(DIST_DIR) and resolved.is_file():
    return FileResponse(resolved)
```

---

### H-02: Webhook 接受未驗證的檔案路徑，可導致任意檔案操作

| 項目 | 內容 |
|------|------|
| **Severity** | High |
| **Files** | `backend/routers/webhook.py:47`, `backend/worker/worker.py:82,155`, `backend/utils/move.py:22` |
| **Category** | Path Traversal / Input Validation |

**Description:**
Webhook `DownloaderOnCompletePayload.filepath` 欄位接受任意字串，直接傳入 `process_completed_download()` 後用於 `shutil.move()` 和 `Path.rename()` 操作，無路徑消毒、無 symlink 解析、無白名單驗證。

**Impact:**
惡意 Webhook 呼叫者可搬移或重新命名伺服器上任何處理程序使用者有權限存取的檔案。

**Recommendation:**
- 驗證 `filepath` 位於預期的下載目錄內。
- 使用 `Path.resolve()` 並以 `is_relative_to()` 確認路徑合法性。

---

### H-03: `move_to` 路徑未驗證，可搬移檔案至任意目錄

| 項目 | 內容 |
|------|------|
| **Severity** | High |
| **Files** | `backend/schemas.py:62-65`, `backend/utils/move.py:5-22` |
| **Category** | Path Traversal / Input Validation |

**Description:**
`TaskCreate` / `TaskUpdate` schema 的 `move_to` 欄位接受任意字串。`move()` 函式會直接以 `mkdir(parents=True)` 建立任意路徑並搬移檔案，未驗證目標路徑是否在 `allowed_directories` 白名單內。

**Recommendation:**
- 在 Task 建立/更新時，驗證 `move_to` 路徑位於 `allowed_directories` 白名單中。

---

### H-04: 使用者自定義 Regex 存在 ReDoS 風險

| 項目 | 內容 |
|------|------|
| **Severity** | High |
| **Files** | `backend/services/preview_service.py:100,121`, `backend/utils/rename.py:53` |
| **Category** | Denial of Service |

**Description:**
```python
pattern = re.compile(pattern, re.IGNORECASE)
```
使用者提供的 regex 模式被直接編譯並執行，無超時限制、無複雜度檢查、無沙箱隔離。惡意或設計不良的 regex（如 `(a+)+$` 對 `"aaaaaaaaaaaa!"`）可導致災難性回溯（Catastrophic Backtracking），凍結伺服器。

**Impact:**
- 單一請求至 `POST /api/v1/preview/regex` 即可導致 worker thread 永久掛起。
- 儲存於資料庫的 rename rule 在每次 Webhook 觸發時執行。

**Recommendation:**
- 使用 Python 3.11+ 的 `re` timeout 功能，或限制 pattern 長度/複雜度。
- 考慮使用 `google-re2` 等不回溯的 regex 引擎。

---

### H-05: 缺少 `.dockerignore` — 整個專案複製進 Docker Image

| 項目 | 內容 |
|------|------|
| **Severity** | High |
| **File** | `Dockerfile:32` |
| **Category** | Information Leakage / Supply Chain |

**Description:**
`COPY . /movera` 在無 `.dockerignore` 的情況下會將 `.git/`、`.env`（若存在）、測試檔案、`node_modules/`、IDE 設定等全部複製進映像檔。

**Recommendation:**
建立 `.dockerignore` 檔案，排除：
```
.git/
.env*
node_modules/
tests/
*.spec.ts
__pycache__/
.vscode/
openspec/
```

---

## Medium

### M-01: Rename `dst` Pattern 可產生路徑穿越檔名

| 項目 | 內容 |
|------|------|
| **Severity** | Medium |
| **File** | `backend/utils/rename.py:34,55` |
| **Category** | Path Traversal |

**Description:**
Regex 替換或 parse 格式化的結果直接作為檔名使用：`filepath.parent.joinpath(renamed)`。若 `dst` 模式產生包含 `../` 的字串，重新命名後的檔案將逃離原始目錄。

**Recommendation:**
驗證產出的檔名不含 `..`、`/` 或絕對路徑元素。

---

### M-02: `PUT /settings` 接受未型別化的 `dict` 本體

| 項目 | 內容 |
|------|------|
| **Severity** | Medium |
| **File** | `backend/routers/setting.py:78` |
| **Category** | Input Validation |

**Description:**
```python
settings: dict
```
設定端點接受裸 `dict`，無 Pydantic schema 驗證，攻擊者可送出任意鍵值對。

**Recommendation:**
定義明確的 `SettingsUpdate` Pydantic schema，僅允許白名單設定項。

---

### M-03: 錯誤訊息洩漏目錄路徑

| 項目 | 內容 |
|------|------|
| **Severity** | Medium |
| **File** | `backend/exceptions/directory_exception.py:8,18` |
| **Category** | Information Leakage |

**Description:**
錯誤訊息包含完整路徑：`f"目錄不存在: '{path}'"` 和 `f"無權存取此目錄: '{path}'"`。這些訊息透過 exception handler 回傳給客戶端，可協助攻擊者確認路徑是否存在。

**Recommendation:**
對外回傳通用錯誤訊息，將詳細路徑僅記錄在伺服器端日誌。

---

### M-04: 缺少全域 Exception Handler（500 錯誤可能洩漏內部資訊）

| 項目 | 內容 |
|------|------|
| **Severity** | Medium |
| **File** | `backend/backend.py` |
| **Category** | Information Leakage |

**Description:**
無 `@app.exception_handler(Exception)` 或 500 錯誤攔截器。FastAPI 預設行為在未處理例外時可能回傳堆疊追蹤和內部細節。

**Recommendation:**
新增全域例外處理器，對外回傳通用錯誤，內部記錄完整堆疊。

---

### M-05: CORS 配置過於寬鬆

| 項目 | 內容 |
|------|------|
| **Severity** | Medium |
| **File** | `backend/middlewares/cors.py:15-21` |
| **Category** | CORS Misconfiguration |

**Description:**
`allow_credentials=True` 搭配 `allow_methods=["*"]` 和 `allow_headers=["*"]` 過於寬鬆。雖然目前 origins 限制在 localhost:5173，但若未來擴展（如設為 `*`），將成為憑證竊取漏洞。

**Recommendation:**
明確列出允許的 methods 和 headers，僅保留必要項目。

---

### M-06: Swagger UI / ReDoc 在正式環境中暴露

| 項目 | 內容 |
|------|------|
| **Severity** | Medium |
| **File** | `backend/backend.py:59-64` |
| **Category** | Information Disclosure |

**Description:**
`FastAPI()` 建構子未設定 `docs_url=None` 或 `redoc_url=None`。`/docs`、`/redoc`、`/openapi.json` 在正式環境中公開暴露完整 API schema。

**Recommendation:**
透過環境變數控制，在正式環境中關閉文件端點。

---

### M-07: 前端通知系統存在潛在 XSS 路徑

| 項目 | 內容 |
|------|------|
| **Severity** | Medium |
| **File** | `src/composables/useNotification.ts:22` |
| **Category** | XSS |

**Description:**
```typescript
description: options?.html && description ? h('div', { innerHTML: description }) : description
```
當 `options.html` 為 `true` 時，`description` 以 `innerHTML` 渲染。目前無呼叫處使用 `{ html: true }`，但此 API 表面存在風險——未來若有開發者搭配 API 錯誤訊息使用，將導致 XSS。

**Recommendation:**
移除 `html` 選項，或在渲染前使用 DOMPurify 消毒。

---

### M-08: Trivy 掃描配置為永不失敗（`exit-code: 0`）

| 項目 | 內容 |
|------|------|
| **Severity** | Medium |
| **File** | `.github/workflows/trivy_scan.yaml:23` |
| **Category** | CI/CD Security |

**Description:**
`exit-code: 0` 使 Trivy 掃描即使發現 Critical/High 漏洞也不會中斷建置流程。

**Recommendation:**
設定 `exit-code: 1` 搭配 `severity: 'CRITICAL,HIGH'` 以阻擋含已知高危漏洞的部署。

---

## Low

### L-01: 字串欄位缺少 `max_length` 限制

| 項目 | 內容 |
|------|------|
| **Severity** | Low |
| **File** | `backend/schemas.py` (多處) |
| **Category** | Input Validation |

**Description:**
`name`、`include`、`move_to`、`pattern`、`value` 等欄位未設定 `max_length`，攻擊者可送出超長字串造成記憶體壓力或資料庫膨脹。

---

### L-02: 伺服器綁定 `0.0.0.0` 監聽所有介面

| 項目 | 內容 |
|------|------|
| **Severity** | Low |
| **Files** | `main.py:41`, `backend/backend.py:132` |
| **Category** | Network Exposure |

**Description:**
`host="0.0.0.0"` 搭配無認證機制，使服務暴露於所有網路介面。

---

### L-03: `alembic.ini` 寫死資料庫路徑

| 項目 | 內容 |
|------|------|
| **Severity** | Low |
| **File** | `alembic.ini:87` |
| **Category** | Information Disclosure |

**Description:**
`sqlalchemy.url = sqlite:///./database/database.db` 寫死在設定檔中，且與 `backend/database.py` 使用環境變數的做法不一致。

---

### L-04: `uv` Binary 使用 `:latest` Tag 未鎖定版本

| 項目 | 內容 |
|------|------|
| **Severity** | Low |
| **File** | `Dockerfile:28` |
| **Category** | Supply Chain |

**Description:**
`COPY --from=ghcr.io/astral-sh/uv:latest` 未固定版本或 digest，建置不具可重現性。

---

### L-05: GitHub Actions 使用主版本 Tag 而非固定 SHA

| 項目 | 內容 |
|------|------|
| **Severity** | Low |
| **Files** | `.github/workflows/builder.yaml`, `tests.yaml`, `trivy_scan.yaml` |
| **Category** | Supply Chain |

**Description:**
`actions/checkout@v6` 等使用版本標籤而非固定 commit SHA，存在供應鏈攻擊風險。

---

### L-06: 前端 Console Error 未在正式環境移除

| 項目 | 內容 |
|------|------|
| **Severity** | Low |
| **Files** | `src/views/CreateTaskView.vue:58`, `src/views/TaskDetailView.vue:83,101,128`, `src/stores/settingStore.ts:24` 等 |
| **Category** | Information Disclosure |

**Description:**
8 處 `console.error()` 在正式環境中可能洩漏內部錯誤細節（堆疊追蹤、API 路徑）。

---

### L-07: 外部連結缺少 `rel="noopener noreferrer"`

| 項目 | 內容 |
|------|------|
| **Severity** | Low |
| **File** | `src/components/ParsePreview.vue:200-204` |
| **Category** | XSS (Tabnabbing) |

**Description:**
`target="_blank"` 的外部連結未設定 `rel="noopener noreferrer"`。

---

## Info (Positive Findings)

| # | Finding | File |
|---|---------|------|
| I-01 | `.gitignore` 正確排除 `.env`、`*.db`、`node_modules/` 等敏感檔案 | `.gitignore` |
| I-02 | 原始碼中未發現寫死的密鑰、密碼或 API Key | 全域掃描 |
| I-03 | `entrypoint.sh` 驗證 PUID/PGID 非零、使用 `gosu` 降權、設定 `set -e` | `entrypoint.sh` |
| I-04 | Vue 模板未使用 `v-html`，所有資料以 `{{ }}` 自動跳脫渲染 | `src/**/*.vue` |
| I-05 | `uv.lock` 包含所有套件的 SHA256 hash，確保依賴完整性 | `uv.lock` |
| I-06 | Docker 使用多階段建置，最終映像不含 Node.js 或 npm | `Dockerfile` |

---

## Remediation Priority Matrix

| Priority | ID | Action | Effort |
|----------|----|--------|--------|
| **P0** | C-01 | 加入 API 認證中介層（API Key / JWT） | Medium |
| **P0** | H-01 | 修復 SPA 路由路徑穿越 — 加入 `resolve()` + `is_relative_to()` 檢查 | Low |
| **P1** | H-02 | Webhook filepath 加入路徑白名單驗證 | Low |
| **P1** | H-03 | Task `move_to` 驗證是否在 `allowed_directories` 內 | Low |
| **P1** | H-04 | Regex 加入超時限制或改用 `google-re2` | Low |
| **P1** | H-05 | 建立 `.dockerignore` 檔案 | Low |
| **P2** | M-01~M-08 | 路徑消毒、輸入驗證強化、CORS 收緊、關閉文件端點 | Medium |
| **P3** | L-01~L-07 | 字串長度限制、版本固定、console 清理 | Low |

---

## Conclusion

Movera v4.2.0 在 SQL Injection 防護（全程使用 ORM）、前端 XSS 防護（無 v-html）、密鑰管理（無寫死密鑰）等方面表現良好。然而，**缺乏認證機制** 是最根本的安全缺陷，使其他所有高風險漏洞的影響被放大。建議優先處理 P0 級別的修復項目，特別是認證機制的導入與路徑穿越漏洞的修補。
