## 1. 前置準備

- [x] 1.1 建立 Alembic migration 腳本，新增 `episode_offset_enabled`（Boolean, 預設 false）、`episode_offset_group`（String, nullable）、`episode_offset_value`（Integer, 預設 0）至 task 表
- [x] 1.2 在 `backend/models/task.py` Task model 新增對應三個欄位
- [x] 1.3 在 `backend/schemas.py` 的 TaskBase、TaskCreate、TaskUpdate、Task schema 新增偏移欄位
- [x] 1.4 在 `src/schemas/index.ts` 前端 TypeScript 介面新增偏移欄位
- [x] 1.5 新增 i18n 翻譯鍵值（`src/locales/` 中文與英文）

## 2. 後端偏移邏輯 — TDD 循環

### 2.1 🔴 紅燈 - 撰寫偏移邏輯測試

- [x] 2.1.1 撰寫 `tests/backend/test_rename.py` 測試：Parse 模式正向偏移（episode `"01"` + 12 = `"13"`）
- [x] 2.1.2 撰寫測試：Regex 模式正向偏移（named group episode `"01"` + 12 = `"13"`）
- [x] 2.1.3 撰寫測試：保持零填充格式（`"003"` + 10 = `"013"`）
- [x] 2.1.4 撰寫測試：偏移後超出原始位數（`"99"` + 5 = `"104"`）
- [x] 2.1.5 撰寫測試：負數偏移量（`"13"` + (-5) = `"08"`）
- [x] 2.1.6 撰寫測試：小數 episode 值偏移（`"07.5"` + 12 = `"19.5"`，保留小數部分與零填充）
- [x] 2.1.7 撰寫測試：小數 episode 值無零填充（`"7.5"` + 5 = `"12.5"`）
- [x] 2.1.8 撰寫測試：Group 值非數字時跳過偏移，使用原始值
- [x] 2.1.9 撰寫測試：偏移未啟用時不影響重新命名流程
- [x] 2.1.10 執行測試，確認全部失敗

### 2.2 🟢 綠燈 - 實作偏移邏輯

- [x] 2.2.1 在 `backend/utils/rename.py` 新增偏移輔助函式 `apply_episode_offset(value: str, offset: int) -> str`（支援整數與小數值，如 `"07.5"` + 12 = `"19.5"`）
- [x] 2.2.2 修改 `Rename.__init__()` 接受偏移參數（`episode_offset_enabled`、`episode_offset_group`、`episode_offset_value`）
- [x] 2.2.3 修改 `Rename.execute_rename()` 在解析群組後、套用 dst_filename 前注入偏移處理
- [x] 2.2.4 處理 Parse 模式：修改 `ParseRenameRule.rename()` 支援群組值覆蓋
- [x] 2.2.5 處理 Regex 模式：修改 `RegexRenameRule.rename()` 支援 named group 偏移
- [x] 2.2.6 執行測試，確認全部通過

### 2.3 🔵 重構 - 優化偏移邏輯

- [x] 2.3.1 檢查偏移邏輯是否有重複程式碼，提取共用邏輯
- [x] 2.3.2 確認錯誤處理（非數字 group 跳過、日誌記錄）完整
- [x] 2.3.3 執行測試，確認仍然通過

## 3. 後端 API Schema — TDD 循環

### 3.1 🔴 紅燈 - 撰寫 API 測試

- [x] 3.1.1 撰寫測試：POST `/api/v1/tasks` 建立任務包含偏移設定，回應包含偏移欄位
- [x] 3.1.2 撰寫測試：PUT `/api/v1/tasks/{task_id}` 更新偏移設定
- [x] 3.1.3 撰寫測試：GET `/api/v1/tasks/{task_id}` 回應包含偏移欄位
- [x] 3.1.4 撰寫測試：偏移量為非整數時 API 回傳驗證錯誤
- [x] 3.1.5 執行測試，確認全部失敗

### 3.2 🟢 綠燈 - 實作 API 支援

- [x] 3.2.1 確認 `backend/schemas.py` 的欄位定義正確（步驟 1.3 已完成）
- [x] 3.2.2 確認 `backend/routers/task.py` 的 create/update 邏輯正確傳遞偏移欄位
- [x] 3.2.3 確認 `backend/repositories/` 的 task repository 正確儲存偏移欄位
- [x] 3.2.4 執行測試，確認全部通過

### 3.3 🔵 重構 - 優化 API 層

- [x] 3.3.1 檢查 schema 欄位描述與範例是否完整
- [x] 3.3.2 執行測試，確認仍然通過

## 4. 前端 UI — TDD 循環

### 4.1 🔴 紅燈 - 撰寫前端測試

- [x] 4.1.1 撰寫 TaskForm 元件測試：rename_rule 為 null 時不顯示 episode 偏移區塊
- [x] 4.1.2 撰寫測試：rename_rule 為 parse/regex 時顯示 episode 偏移開關
- [x] 4.1.3 撰寫測試：開關啟用後顯示 group 下拉選單與偏移量輸入
- [x] 4.1.4 撰寫測試：偏移量欄位僅接受整數
- [x] 4.1.5 執行測試，確認全部失敗

### 4.2 🟢 綠燈 - 實作前端 UI

- [x] 4.2.1 在 `src/components/TaskForm.vue` 新增 episode 偏移區塊（Checkbox + Select + NumberInput）
- [x] 4.2.2 從 src_filename pattern 自動解析出的 groups 作為下拉選單選項
- [x] 4.2.3 綁定 v-model 至 form 資料，確保與 API 欄位對應
- [x] 4.2.4 實作條件顯示邏輯（rename_rule 不為 null 時才顯示，開關啟用才顯示詳細設定）
- [x] 4.2.5 偏移量 input 限制為整數輸入
- [x] 4.2.6 執行測試，確認全部通過

### 4.3 🔵 重構 - 優化前端程式碼

- [x] 4.3.1 檢查 UI 佈局與現有 TaskForm 風格一致
- [x] 4.3.2 確認 i18n 翻譯完整
- [x] 4.3.3 執行測試，確認仍然通過

## 5. 整合測試與 E2E 驗證

- [x] 5.1 執行完整後端測試套件 `pytest`，確認無回歸
- [x] 5.2 執行完整前端測試套件 `vitest`，確認無回歸
- [x] 5.3 啟動開發伺服器，使用 MCP Chrome DevTools 進行 E2E 驗證：建立任務 → 設定偏移 → 儲存 → 重新載入確認資料持久化

## 6. 程式碼品質檢查

- [x] 6.1 執行 `ruff check` 與 `ruff format` 確認後端程式碼品質
- [x] 6.2 執行前端 lint 與 type check
- [x] 6.3 確認 Alembic migration 可正確升級與降級
