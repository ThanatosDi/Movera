## 1. 前置準備

- [x] 1.1 建立 `backend/utils/path_security.py` 骨架（空函式 `validate_path_within`、`sanitize_filename`）
- [x] 1.2 建立 `backend/middlewares/auth.py` 骨架（空的 `setup_api_key_auth` 函式）
- [x] 1.3 新增 i18n 翻譯 key（認證錯誤、路徑驗證錯誤、Regex 超時錯誤相關訊息）

## 2. 路徑安全工具函式（TDD 循環）

### 2.1 🔴 紅燈 - 撰寫路徑安全工具測試

- [x] 2.1.1 測試：`validate_path_within` 正常路徑回傳 True
- [x] 2.1.2 測試：`validate_path_within` 含 `..` 路徑穿越回傳 False
- [x] 2.1.3 測試：`validate_path_within` 路徑不在允許範圍內回傳 False
- [x] 2.1.4 測試：`sanitize_filename` 正常檔名通過驗證
- [x] 2.1.5 測試：`sanitize_filename` 含 `../` 的檔名引發錯誤
- [x] 2.1.6 測試：`sanitize_filename` 含路徑分隔符 `/` 或 `\` 的檔名引發錯誤
- [x] 2.1.7 執行測試，確認全部失敗

### 2.2 🟢 綠燈 - 實作路徑安全工具

- [x] 2.2.1 實作 `validate_path_within(path, allowed_bases)` — resolve + is_relative_to 檢查
- [x] 2.2.2 實作 `sanitize_filename(name)` — 拒絕含 `..`、`/`、`\` 的檔名
- [x] 2.2.3 執行測試，確認全部通過

### 2.3 🔵 重構 - 確認工具函式品質

- [x] 2.3.1 確認邊界案例處理正確（空字串、None、符號連結等）
- [x] 2.3.2 執行測試，確認仍然通過

## 3. SPA 路由路徑穿越修復（TDD 循環）

### 3.1 🔴 紅燈 - 撰寫 SPA 路由測試

- [x] 3.1.1 測試：正常靜態檔案路徑回傳該檔案
- [x] 3.1.2 測試：含 `..` 的路徑不回傳目標檔案（回傳 index.html fallback）
- [x] 3.1.3 執行測試，確認失敗

### 3.2 🟢 綠燈 - 修復 SPA 路由

- [x] 3.2.1 修改 `main.py` 的 `serve_spa`，加入 `resolve()` + `is_relative_to(DIST_DIR)` 檢查
- [x] 3.2.2 執行測試，確認全部通過

### 3.3 🔵 重構 - 確認路由品質

- [x] 3.3.1 確認使用 `path_security.validate_path_within` 統一邏輯
- [x] 3.3.2 執行測試，確認仍然通過

## 4. Webhook 與 Task 路徑驗證（TDD 循環）

### 4.1 🔴 紅燈 - 撰寫路徑驗證測試

- [x] 4.1.1 測試：Webhook worker 拒絕含路徑穿越的 filepath
- [x] 4.1.2 測試：Webhook worker 拒絕不存在的 filepath
- [x] 4.1.3 測試：Webhook worker 接受合法的 filepath
- [x] 4.1.4 測試：Task Service 建立任務時拒絕 move_to 不在白名單內
- [x] 4.1.5 測試：Task Service 建立任務時接受 move_to 在白名單內
- [x] 4.1.6 測試：Task Service 更新任務時同樣驗證 move_to
- [x] 4.1.7 執行測試，確認全部失敗

### 4.2 🟢 綠燈 - 實作路徑驗證

- [x] 4.2.1 修改 `backend/worker/worker.py`，在 `process_completed_download` 中加入 filepath 驗證
- [x] 4.2.2 修改 `backend/services/task_service.py`，在建立/更新任務時驗證 move_to 路徑
- [x] 4.2.3 執行測試，確認全部通過

### 4.3 🔵 重構 - 確認驗證邏輯品質

- [x] 4.3.1 確認錯誤訊息明確且不洩漏內部路徑
- [x] 4.3.2 執行測試，確認仍然通過

## 5. Rename 檔名路徑穿越防護（TDD 循環）

### 5.1 🔴 紅燈 - 撰寫 Rename 安全測試

- [x] 5.1.1 測試：ParseRenameRule 正常檔名重新命名成功
- [x] 5.1.2 測試：ParseRenameRule 產出含 `../` 的檔名引發錯誤
- [x] 5.1.3 測試：RegexRenameRule 產出含路徑分隔符的檔名引發錯誤
- [x] 5.1.4 執行測試，確認全部失敗

### 5.2 🟢 綠燈 - 實作 Rename 安全防護

- [x] 5.2.1 修改 `backend/utils/rename.py`，在 rename 執行前呼叫 `sanitize_filename` 驗證產出檔名
- [x] 5.2.2 執行測試，確認全部通過

### 5.3 🔵 重構 - 確認 Rename 品質

- [x] 5.3.1 確認 ParseRenameRule 和 RegexRenameRule 共用相同的檔名驗證邏輯
- [x] 5.3.2 執行測試，確認仍然通過

## 6. Regex 超時防護（TDD 循環）

### 6.1 🔴 紅燈 - 撰寫 Regex 超時測試

- [x] 6.1.1 測試：`RegexPreviewService._match` 正常 pattern 在限時內回傳結果
- [x] 6.1.2 測試：`RegexPreviewService._match` 惡意 pattern 超時引發 TimeoutError 或自訂錯誤
- [x] 6.1.3 測試：`RegexPreviewService._format` 惡意 pattern 超時引發錯誤
- [x] 6.1.4 測試：`RegexRenameRule.rename` 超時時引發錯誤
- [x] 6.1.5 執行測試，確認全部失敗

### 6.2 🟢 綠燈 - 實作 Regex 超時

- [x] 6.2.1 修改 `backend/services/preview_service.py`，所有 `re.compile` 和 `re.sub` 加入 `timeout=2`
- [x] 6.2.2 修改 `backend/utils/rename.py`，`re.compile` 和 `re.sub` 加入 `timeout=2`
- [x] 6.2.3 修改 `backend/routers/preview.py`，捕捉 `re.error` / `TimeoutError` 回傳 HTTP 422
- [x] 6.2.4 執行測試，確認全部通過

### 6.3 🔵 重構 - 確認 Regex 超時品質

- [x] 6.3.1 確認超時常數集中定義（如 `REGEX_TIMEOUT_SECONDS = 2`）
- [x] 6.3.2 執行測試，確認仍然通過

## 7. API Key 認證中介層（TDD 循環）

### 7.1 🔴 紅燈 - 撰寫認證中介層測試

- [x] 7.1.1 測試：`MOVERA_API_KEY` 已設定時，無 header 的請求回傳 401
- [x] 7.1.2 測試：`MOVERA_API_KEY` 已設定時，錯誤 key 的請求回傳 401
- [x] 7.1.3 測試：`MOVERA_API_KEY` 已設定時，正確 `Authorization: Bearer <key>` 的請求通過
- [x] 7.1.4 測試：`MOVERA_API_KEY` 已設定時，正確 `X-API-Key: <key>` 的請求通過
- [x] 7.1.5 測試：`MOVERA_API_KEY` 未設定時，所有請求通過（向下相容）
- [x] 7.1.6 測試：靜態資源路由不受認證保護
- [x] 7.1.7 執行測試，確認全部失敗

### 7.2 🟢 綠燈 - 實作認證中介層

- [x] 7.2.1 實作 `backend/middlewares/auth.py` 的 `setup_api_key_auth` Middleware
- [x] 7.2.2 在 `backend/backend.py` 中註冊認證 Middleware
- [x] 7.2.3 執行測試，確認全部通過

### 7.3 🔵 重構 - 確認認證品質

- [x] 7.3.1 確認認證失敗回應不洩漏 API Key 資訊
- [x] 7.3.2 確認 timing-safe 比對（避免 timing attack）
- [x] 7.3.3 執行測試，確認仍然通過

## 8. 全域錯誤處理與資訊洩漏修復（TDD 循環）

### 8.1 🔴 紅燈 - 撰寫錯誤處理測試

- [x] 8.1.1 測試：未預期例外回傳 HTTP 500 + 固定 body
- [x] 8.1.2 測試：DirectoryNotFound 錯誤訊息不含完整路徑
- [x] 8.1.3 測試：DirectoryAccessDenied 錯誤訊息不含完整路徑
- [x] 8.1.4 執行測試，確認全部失敗

### 8.2 🟢 綠燈 - 實作錯誤處理修復

- [x] 8.2.1 在 `backend/backend.py` 新增全域 `@app.exception_handler(Exception)` handler
- [x] 8.2.2 修改 `backend/exceptions/directory_exception.py`，`__str__` 回傳通用訊息，新增 `log_message` 屬性保留完整路徑
- [x] 8.2.3 修改 `backend/backend.py` 中 directory exception handler，用 loguru 記錄 `exc.log_message`
- [x] 8.2.4 執行測試，確認全部通過

### 8.3 🔵 重構 - 確認錯誤處理品質

- [x] 8.3.1 確認所有 exception handler 一致性
- [x] 8.3.2 執行測試，確認仍然通過

## 9. 輸入驗證強化（TDD 循環）

### 9.1 🔴 紅燈 - 撰寫輸入驗證測試

- [x] 9.1.1 測試：`SettingsUpdate` schema 接受合法欄位
- [x] 9.1.2 測試：`SettingsUpdate` schema 拒絕非白名單欄位
- [x] 9.1.3 測試：Task name 超過 255 字元被 schema 拒絕
- [x] 9.1.4 測試：Task move_to 超過 1024 字元被 schema 拒絕
- [x] 9.1.5 測試：PresetRule pattern 超過 1024 字元被 schema 拒絕
- [x] 9.1.6 執行測試，確認全部失敗

### 9.2 🟢 綠燈 - 實作輸入驗證

- [x] 9.2.1 在 `backend/schemas.py` 新增 `SettingsUpdate` Pydantic schema
- [x] 9.2.2 修改 `backend/routers/setting.py` 使用 `SettingsUpdate` 取代裸 `dict`
- [x] 9.2.3 在 `backend/schemas.py` 所有字串欄位加入 `max_length`（name: 255, path/pattern: 1024）
- [x] 9.2.4 執行測試，確認全部通過

### 9.3 🔵 重構 - 確認驗證品質

- [x] 9.3.1 確認前端 TypeScript schema 與後端 max_length 一致
- [x] 9.3.2 執行測試，確認仍然通過

## 10. CORS 收緊與 Swagger UI 控制

- [x] 10.1 修改 `backend/middlewares/cors.py`，`allow_methods` 改為 `["GET", "POST", "PUT", "DELETE", "OPTIONS"]`
- [x] 10.2 修改 `backend/middlewares/cors.py`，`allow_headers` 改為 `["Content-Type", "Authorization", "X-API-Key"]`
- [x] 10.3 修改 `backend/backend.py`，FastAPI 建構子依 `MOVERA_ENABLE_DOCS` 環境變數控制 docs_url/redoc_url/openapi_url
- [x] 10.4 執行後端測試套件，確認無回歸

## 11. 前端安全修復

- [x] 11.1 修改 `src/composables/useNotification.ts`，移除 `innerHTML` 渲染路徑，description 僅以純文字渲染
- [x] 11.2 修改 `src/schemas/index.ts`，移除 `NotificationOptions` 的 `html` 欄位
- [x] 11.3 修改 `src/components/ParsePreview.vue`，外部連結加入 `rel="noopener noreferrer"`
- [x] 11.4 前端 `useHttpService` composable 加入 `X-API-Key` header 支援
- [x] 11.5 執行前端測試套件，確認無回歸

## 12. 基礎設施修復

- [x] 12.1 建立 `.dockerignore` 檔案，排除 `.git/`、`.env*`、`node_modules/`、`tests/`、`__pycache__/`、`.vscode/`、`openspec/`
- [x] 12.2 修改 `Dockerfile`，`uv` image 鎖定具體版本 tag（取代 `:latest`）
- [x] 12.3 修改 `alembic.ini`，資料庫路徑改用環境變數插值
- [x] 12.4 修改 `.github/workflows/trivy_scan.yaml`，`exit-code` 改為 `1`

## 13. 整合測試與品質檢查

- [x] 13.1 執行完整後端測試套件（`pytest`），確認無回歸
- [x] 13.2 執行完整前端測試套件（`vitest`），確認無回歸
- [x] 13.3 執行 `vue-tsc` 型別檢查，確認無錯誤
- [x] 13.4 使用 MCP Chrome DevTools 進行 E2E 測試：驗證認證啟用後前端仍可正常存取
- [x] 13.5 使用 MCP Chrome DevTools 進行 E2E 測試：驗證設定頁面功能正常
