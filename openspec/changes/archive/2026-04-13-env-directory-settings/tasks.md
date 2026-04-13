## 1. 前置準備

- [x] 1.1 確認現有測試全部通過（`uv run pytest tests/` 和 `npx vitest run`）
- [x] 1.2 閱讀現有 `SettingService`、`setting` router、`SettingView.vue`、`settingStore.ts` 程式碼

## 2. 後端 — 環境變數解析模組

### 2.1 🔴 紅燈 — 撰寫環境變數解析測試

- [x] 2.1.1 撰寫測試：解析 `ALLOWED_DIRECTORIES=/downloads,/media` 回傳 `["/downloads", "/media"]`
- [x] 2.1.2 撰寫測試：環境變數未設定或為空字串時回傳空陣列
- [x] 2.1.3 撰寫測試：忽略相對路徑，僅保留絕對路徑
- [x] 2.1.4 撰寫測試：解析 `ALLOWED_SOURCE_DIRECTORIES` 同理
- [x] 2.1.5 撰寫測試：解析 `ALLOW_WEBUI_SETTING=false` 回傳 `False`，未設定或 `true` 時回傳 `True`
- [x] 2.1.6 執行測試，確認全部失敗

### 2.2 🟢 綠燈 — 實作環境變數解析

- [x] 2.2.1 建立 `backend/utils/env_config.py` 模組
- [x] 2.2.2 實作 `get_env_allowed_directories()` 函式
- [x] 2.2.3 實作 `get_env_allowed_source_directories()` 函式
- [x] 2.2.4 實作 `get_allow_webui_setting()` 函式
- [x] 2.2.5 執行測試，確認全部通過

### 2.3 🔵 重構 — 優化環境變數解析

- [x] 2.3.1 提取共用的逗號分隔路徑解析邏輯
- [x] 2.3.2 執行測試，確認仍然通過

## 3. 後端 — SettingService 合併環境變數項目

### 3.1 🔴 紅燈 — 撰寫合併邏輯測試

- [x] 3.1.1 撰寫測試：`get_all_settings()` 回傳的 `allowed_directories` 合併環境變數與資料庫項目，每項包含 `path` 和 `source`
- [x] 3.1.2 撰寫測試：環境變數與資料庫重複時，以環境變數為優先（`source: "env"`）
- [x] 3.1.3 撰寫測試：`get_all_settings()` 回傳包含 `allow_webui_setting` 布林值
- [x] 3.1.4 撰寫測試：`update_settings()` 中環境變數項目不可被刪除（自動保留）
- [x] 3.1.5 撰寫測試：`get_allowed_directories()` 合併環境變數回傳完整路徑陣列
- [x] 3.1.6 撰寫測試：`get_allowed_source_directories()` 合併環境變數回傳完整路徑陣列
- [x] 3.1.7 執行測試，確認全部失敗

### 3.2 🟢 綠燈 — 實作合併邏輯

- [x] 3.2.1 修改 `get_all_settings()` 合併環境變數項目，回傳 `{path, source}[]` 結構
- [x] 3.2.2 修改 `get_all_settings()` 加入 `allow_webui_setting` 欄位
- [x] 3.2.3 修改 `update_settings()` 保護環境變數項目不被刪除
- [x] 3.2.4 修改 `get_allowed_directories()` 合併環境變數
- [x] 3.2.5 修改 `get_allowed_source_directories()` 合併環境變數
- [x] 3.2.6 執行測試，確認全部通過

### 3.3 🔵 重構 — 優化 SettingService

- [x] 3.3.1 檢查合併邏輯是否可提取為共用方法
- [x] 3.3.2 執行測試，確認仍然通過

## 4. 後端 — API 層 ALLOW_WEBUI_SETTING 攔截

### 4.1 🔴 紅燈 — 撰寫 Router 測試

- [x] 4.1.1 撰寫測試：`ALLOW_WEBUI_SETTING=false` 時 `PUT /api/v1/settings` 包含 `allowed_directories` 回傳 403
- [x] 4.1.2 撰寫測試：`ALLOW_WEBUI_SETTING=false` 時 `PUT /api/v1/settings` 包含 `allowed_source_directories` 回傳 403
- [x] 4.1.3 撰寫測試：`ALLOW_WEBUI_SETTING=false` 時 `PUT /api/v1/settings` 不包含目錄設定的其他欄位正常更新
- [x] 4.1.4 撰寫測試：`ALLOW_WEBUI_SETTING=true` 時正常更新所有設定
- [x] 4.1.5 執行測試，確認全部失敗

### 4.2 🟢 綠燈 — 實作 Router 攔截

- [x] 4.2.1 在 `update_settings()` router 中加入 `ALLOW_WEBUI_SETTING` 檢查
- [x] 4.2.2 執行測試，確認全部通過

### 4.3 🔵 重構

- [x] 4.3.1 執行測試，確認仍然通過

## 5. 前端 — Schema 與 Store 更新

### 5.1 🟢 綠燈 — 實作前端資料結構變更

- [x] 5.1.1 更新 `src/schemas/index.ts`：`allowed_directories` 和 `allowed_source_directories` 型別改為 `{path: string, source: 'env' | 'db'}[]`
- [x] 5.1.2 新增 `allow_webui_setting` 布林欄位至 Settings interface
- [x] 5.1.3 更新 `settingStore.ts` 初始值
- [x] 5.1.4 執行前端型別檢查 `npx vue-tsc --noEmit`

## 6. 前端 — 設定頁面 UI 更新

### 6.1 🟢 綠燈 — 實作 UI 變更

- [x] 6.1.1 更新 `SettingView.vue` 的 `allowed_directories` 列表：環境變數項目顯示鎖頭圖示、隱藏刪除按鈕
- [x] 6.1.2 更新 `SettingView.vue` 的 `allowed_source_directories` 列表：同上邏輯
- [x] 6.1.3 `ALLOW_WEBUI_SETTING=false` 時隱藏兩個 card 的新增輸入框
- [x] 6.1.4 更新 `addDirectory()`/`removeDirectory()` 邏輯，適配新資料結構 `{path, source}`
- [x] 6.1.5 更新 `addSourceDirectory()`/`removeSourceDirectory()` 邏輯，同上
- [x] 6.1.6 更新 `UpdateSettings()` 送出時僅傳送 `db` 來源的項目路徑
- [x] 6.1.7 新增 i18n 翻譯 key（`lockedByEnv`、`webuiSettingDisabled` 等）
- [x] 6.1.8 執行前端型別檢查與建置 `npx vue-tsc --noEmit && npm run build`

### 6.2 🔵 重構

- [x] 6.2.1 檢查 `allowed_directories` 和 `allowed_source_directories` 的列表 UI 是否可提取為共用元件
- [x] 6.2.2 執行前端型別檢查，確認仍然通過

## 7. 部署文件

- [x] 7.1 建立或更新 `.env.example`，新增 `ALLOWED_DIRECTORIES`、`ALLOWED_SOURCE_DIRECTORIES`、`ALLOW_WEBUI_SETTING` 說明

## 8. 整合測試與品質檢查

- [x] 8.1 執行全部後端測試 `uv run pytest tests/ -v`
- [x] 8.2 執行全部前端測試與型別檢查
- [x] 8.3 啟動開發伺服器，在瀏覽器中驗證：環境變數項目鎖定、`ALLOW_WEBUI_SETTING=false` 時 UI 唯讀
- [x] 8.4 執行 `uv run ruff check backend/` 確認無 lint 錯誤
- [x] 8.5 執行 `npx vue-tsc --noEmit` 確認前端型別正確
