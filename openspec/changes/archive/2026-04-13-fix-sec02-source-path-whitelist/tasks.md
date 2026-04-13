## 1. 前置準備

- [x] 1.1 確認現有測試全部通過（`uv run pytest tests/` 和 `npx vitest run`）
- [x] 1.2 閱讀 `SettingService`、`worker.py`、`SettingView.vue`、`settingStore.ts` 現有程式碼

## 2. 後端 — SettingService 支援 `allowed_source_directories`

### 2.1 🔴 紅燈 — 撰寫 SettingService 測試

- [x] 2.1.1 撰寫測試：`get_allowed_source_directories()` 在設定存在時回傳解析後的路徑陣列
- [x] 2.1.2 撰寫測試：`get_allowed_source_directories()` 在設定不存在時回傳空陣列
- [x] 2.1.3 撰寫測試：`allowed_source_directories` 在 `get_all_settings()` 中被反序列化為原生陣列
- [x] 2.1.4 撰寫測試：`update_settings()` 中 `allowed_source_directories` 包含相對路徑時拋出 `ValueError`
- [x] 2.1.5 執行測試，確認全部失敗

### 2.2 🟢 綠燈 — 實作 SettingService 功能

- [x] 2.2.1 在 `_JSON_FIELDS` 中加入 `"allowed_source_directories"`
- [x] 2.2.2 新增 `get_allowed_source_directories()` 方法
- [x] 2.2.3 在 `update_settings()` 中加入 `allowed_source_directories` 的絕對路徑驗證
- [x] 2.2.4 執行測試，確認全部通過

### 2.3 🔵 重構 — 優化 SettingService 程式碼

- [x] 2.3.1 檢查 `get_allowed_source_directories()` 與 `get_allowed_directories()` 是否可提取共用邏輯
- [x] 2.3.2 執行測試，確認仍然通過

## 3. 後端 — Worker 路徑驗證

### 3.1 🔴 紅燈 — 撰寫 Worker 測試

- [x] 3.1.1 撰寫測試：`is_path_within_allowed()` 路徑在白名單範圍內回傳 `True`
- [x] 3.1.2 撰寫測試：`is_path_within_allowed()` 路徑不在白名單範圍內回傳 `False`
- [x] 3.1.3 撰寫測試：`is_path_within_allowed()` 空白名單回傳 `False`
- [x] 3.1.4 撰寫測試：`process_completed_download()` 白名單設定後，路徑不在範圍內時拒絕處理
- [x] 3.1.5 撰寫測試：`process_completed_download()` 白名單設定後，路徑在範圍內時正常處理
- [x] 3.1.6 撰寫測試：`process_completed_download()` 白名單為空時允許所有路徑（向後相容）
- [x] 3.1.7 執行測試，確認全部失敗

### 3.2 🟢 綠燈 — 實作 Worker 路徑驗證

- [x] 3.2.1 在 `WorkerServices` dataclass 中加入 `setting_service: SettingService`
- [x] 3.2.2 更新 `create_worker_services()` 工廠函式，建立 `SettingService` 實例
- [x] 3.2.3 新增 `is_path_within_allowed()` 函式
- [x] 3.2.4 在 `process_completed_download()` 開頭加入白名單驗證邏輯
- [x] 3.2.5 更新既有測試的 `mock_services` fixture，加入 `setting_service` mock
- [x] 3.2.6 執行測試，確認全部通過

### 3.3 🔵 重構 — 優化 Worker 程式碼

- [x] 3.3.1 確認日誌訊息格式一致
- [x] 3.3.2 執行測試，確認仍然通過

## 4. 前端 — Settings Schema 與 Store

### 4.1 🔴 紅燈 — 撰寫 Store 測試（如適用）

- [x] 4.1.1 確認 `settingStore` 的 `fetchSettings()` 和 `updateSettings()` 正確處理新欄位

### 4.2 🟢 綠燈 — 實作 Schema 與 Store 變更

- [x] 4.2.1 在 `src/schemas/` 的 Settings schema 中加入 `allowed_source_directories?: string[]` 欄位
- [x] 4.2.2 確認 `settingStore.ts` 的 `fetchSettings()` 和 `updateSettings()` 無需修改（已為泛用）
- [x] 4.2.3 執行前端型別檢查 `npx vue-tsc --noEmit`

## 5. 前端 — 設定頁面 UI

### 5.1 🔴 紅燈 — 定義 UI 行為

- [x] 5.1.1 確認 i18n key 規劃：`settingView.allowedSourceDirectoriesCard.*`

### 5.2 🟢 綠燈 — 實作設定頁面 UI

- [x] 5.2.1 在 `SettingView.vue` 新增「檔案來源白名單」card 區塊
- [x] 5.2.2 實作輸入框 + 絕對路徑驗證（與 `allowed_directories` 相同邏輯）
- [x] 5.2.3 實作路徑列表顯示與移除功能
- [x] 5.2.4 白名單為空時顯示安全提示文字
- [x] 5.2.5 新增 i18n 翻譯 key（`zh-TW.json` 和 `en.json`）
- [x] 5.2.6 執行前端型別檢查與建置 `npx vue-tsc --noEmit && npm run build`

### 5.3 🔵 重構 — 優化前端程式碼

- [x] 5.3.1 檢查 `allowed_directories` 與 `allowed_source_directories` 的 UI 邏輯是否可提取為共用元件或函式
- [x] 5.3.2 執行前端型別檢查，確認仍然通過

## 6. 整合測試與驗證

- [x] 6.1 執行全部後端測試 `uv run pytest tests/ -v`
- [x] 6.2 執行全部前端測試與型別檢查
- [x] 6.3 啟動開發伺服器，在瀏覽器中驗證設定頁面 UI
- [x] 6.4 驗證 Webhook 白名單攔截功能（透過 API 測試）

## 7. 程式碼品質檢查

- [x] 7.1 執行 `uv run ruff check backend/` 確認無 lint 錯誤
- [x] 7.2 執行 `npx vue-tsc --noEmit` 確認前端型別正確
