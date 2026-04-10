## ADDED Requirements

### Requirement: Backend 模組命名遵循 PEP 8
所有 Backend Python 模組檔案 SHALL 使用 snake_case 命名。禁止使用 camelCase 作為模組檔名。

#### Scenario: Service 模組檔案命名
- **WHEN** 檢查 `backend/services/` 目錄中的所有 `.py` 檔案
- **THEN** 所有檔案名稱 SHALL 為 snake_case 格式（例如 `task_service.py`，非 `taskService.py`）

#### Scenario: Exception 模組檔案命名
- **WHEN** 檢查 `backend/exceptions/` 目錄中的所有 `.py` 檔案
- **THEN** 所有檔案名稱 SHALL 為 snake_case 格式（例如 `task_exception.py`，非 `taskException.py`）

### Requirement: 所有函式必須具備完整型別提示
所有 Backend Python 函式 SHALL 包含參數型別提示與回傳型別提示。所有 Frontend TypeScript 函式 SHALL 避免使用 `any` 型別。

#### Scenario: Backend 函式回傳型別
- **WHEN** 檢查 `backend/services/` 與 `backend/repositories/` 中的所有公開方法
- **THEN** 每個方法 SHALL 具備明確的回傳型別標註（`-> Type`）

#### Scenario: Frontend 禁止 any 型別
- **WHEN** 檢查 `src/` 目錄中的所有 `.ts` 與 `.vue` 檔案（排除測試檔案與 `components/ui/`）
- **THEN** 不 SHALL 存在 `any` 型別的使用

### Requirement: 統一依賴注入模式
所有 Backend Router 端點 SHALL 透過 FastAPI `Depends()` 機制取得 Service 實例，禁止在路由函式中直接實例化 Service。

#### Scenario: Preview 路由使用依賴注入
- **WHEN** 檢查 `backend/routers/preview.py` 中的路由函式
- **THEN** 所有 Service 實例 SHALL 透過 `Depends()` 參數注入，而非在函式內部使用 `Service()` 建構

#### Scenario: 所有路由統一注入模式
- **WHEN** 檢查 `backend/routers/` 中的所有路由檔案
- **THEN** 無任何路由函式 SHALL 直接呼叫 Service 建構子

### Requirement: rename 工具函式無變數作用域錯誤
`backend/utils/rename.py` 中的所有 rename 類別 SHALL 正確處理 `str` 與 `Path` 兩種型別的 `filepath` 參數，不 SHALL 產生 `NameError`。

#### Scenario: filepath 為 Path 物件時正常運作
- **WHEN** 以 `Path` 物件呼叫 `ParseRenameRule.rename()` 或 `RegexRenameRule.rename()`
- **THEN** SHALL 正確回傳重新命名後的檔案名稱，無 `NameError` 異常

#### Scenario: filepath 為 str 時正常運作
- **WHEN** 以 `str` 呼叫 `ParseRenameRule.rename()` 或 `RegexRenameRule.rename()`
- **THEN** SHALL 正確回傳重新命名後的檔案名稱

### Requirement: Service 遵循單一職責原則
每個 Service 類別 SHALL 僅負責單一領域的商業邏輯。路徑驗證 SHALL 獨立於目錄掃描與設定管理。

#### Scenario: PathService 拆分後的職責
- **WHEN** 檢查 `backend/services/directory_service.py`
- **THEN** SHALL 僅包含目錄列表、掃描相關方法，不 SHALL 包含路徑安全驗證邏輯

#### Scenario: 路徑驗證獨立存在
- **WHEN** 檢查 `backend/utils/` 中的路徑驗證模組
- **THEN** SHALL 存在獨立的路徑驗證函式，可被多個 Service 重用

### Requirement: Worker 不使用全域可變狀態
`backend/worker/worker.py` SHALL 不使用模組層級的全域可變狀態（`global` 關鍵字）來管理服務實例。服務依賴 SHALL 透過函式參數傳入。

#### Scenario: Worker 函式接收服務依賴
- **WHEN** 檢查 `process_completed_download` 函式
- **THEN** 服務依賴 SHALL 透過參數傳入，而非透過 `global` 變數存取

#### Scenario: 無全域可變狀態
- **WHEN** 搜尋 `backend/worker/worker.py` 中的 `global` 關鍵字
- **THEN** SHALL 不存在任何 `global` 變數宣告

### Requirement: Frontend 元件長度限制
單一 Vue 元件檔案 SHALL 不超過 200 行（含模板）。超過限制時 SHALL 拆分為子元件。

#### Scenario: TaskDetailView 拆分
- **WHEN** 檢查 `src/views/TaskDetailView.vue`
- **THEN** 檔案行數 SHALL 不超過 200 行
- **THEN** SHALL 存在 `TaskEditForm.vue`、`TaskLogsPanel.vue`、`TaskDeleteDialog.vue` 子元件

### Requirement: Frontend 事件處理器命名一致
所有 Vue 元件中的事件處理器函式 SHALL 使用 `handle` 前綴命名（例如 `handleDelete`、`handleSubmit`）。禁止使用 `btn*`、`on*` 作為處理器函式名稱。

#### Scenario: 事件處理器命名檢查
- **WHEN** 檢查 `src/views/` 與 `src/components/` 中的事件處理器函式
- **THEN** 所有處理器函式 SHALL 以 `handle` 為前綴

### Requirement: 複雜商業邏輯必須附帶 Why 註解
包含條件分支、正則表達式、或非直覺實作的函式 SHALL 使用 docstring（Python）或 JSDoc（TypeScript）說明「為什麼」選擇此實作方式。

#### Scenario: Backend 複雜邏輯註解
- **WHEN** 檢查 `backend/services/` 與 `backend/utils/` 中包含 3 個以上條件分支的函式
- **THEN** 該函式 SHALL 具備 docstring，包含 Why 說明

#### Scenario: Frontend 複雜邏輯註解
- **WHEN** 檢查 `src/composables/` 與 `src/stores/` 中的複雜函式
- **THEN** 該函式 SHALL 具備 JSDoc 註解，包含 Why 說明

### Requirement: 禁止未使用的 import
所有 Python 與 TypeScript 檔案 SHALL 不包含未使用的 import 語句。

#### Scenario: Backend 無未使用 import
- **WHEN** 對 `backend/` 執行靜態分析或 linter 檢查
- **THEN** SHALL 不存在未使用的 import 語句

#### Scenario: Frontend 無未使用 import
- **WHEN** 對 `src/` 執行 TypeScript 編譯檢查（`noUnusedLocals` 已啟用）
- **THEN** SHALL 不存在未使用的 import 語句
