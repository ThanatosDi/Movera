## 1. 前置準備

- [x] 1.1 將 `h:/VSCode/Python/Movera` 的完整程式碼複製到 `h:/VSCode/Python/Movera.v2` 對應目錄（backend/、src/、tests/、main.py、migration/、pyproject.toml、package.json 等）
- [x] 1.2 確認現有測試套件全部通過（`pytest` + `vitest run`），建立重構基準線

## 2. 修復 rename.py 變數作用域 Bug

### 2.1 🔴 紅燈 - 撰寫 rename Bug 修復測試
- [x] 在 `tests/backend/test_utils_rename.py` 新增測試：以 `Path` 物件呼叫 `ParseRenameRule.rename()`，預期正常回傳
- [x] 在 `tests/backend/test_utils_rename.py` 新增測試：以 `Path` 物件呼叫 `RegexRenameRule.rename()`，預期正常回傳
- [x] 執行測試，確認新增的測試案例失敗（觸發 `NameError`）

### 2.2 🟢 綠燈 - 修復 rename.py 變數作用域
- [x] 修正 `ParseRenameRule.rename()`：將 `filepath = Path(self.filepath) if isinstance(self.filepath, str) else self.filepath` 替換原本的 if 區塊
- [x] 修正 `RegexRenameRule.rename()`：同上處理
- [x] 執行測試，確認全部通過

### 2.3 🔵 重構 - 優化 rename.py 程式碼
- [x] 提取 filepath 轉換邏輯為共用方法或基礎類別方法 `_ensure_path()`
- [x] 為 `ParseRenameRule`、`RegexRenameRule`、`Rename` 類別補充 docstring（含 Why 說明）
- [x] 執行測試，確認仍然通過

## 3. Backend 模組重新命名（snake_case）

### 3.1 🔴 紅燈 - 撰寫 import 路徑驗證測試
- [x] 在 `tests/backend/` 新增 `test_module_naming.py`，驗證所有 Service 可從 snake_case 路徑正確匯入
- [x] 執行測試，確認失敗（檔案尚未重新命名）

### 3.2 🟢 綠燈 - 執行批量重新命名
- [x] 重新命名 `backend/services/` 下所有檔案：`taskService.py` → `task_service.py`、`settingService.py` → `setting_service.py`、`previewService.py` → `preview_service.py`、`pathService.py` → `path_service.py`、`logService.py` → `log_service.py`
- [x] 重新命名 `backend/exceptions/` 下所有檔案：`taskException.py` → `task_exception.py`、`directoryException.py` → `directory_exception.py`、`workerException.py` → `worker_exception.py`
- [x] 更新所有受影響的 import 路徑：`backend/routers/*.py`、`backend/dependencies.py`、`backend/backend.py`、`backend/worker/worker.py`
- [x] 更新所有測試檔案的 import 路徑：`tests/backend/*.py`
- [x] 執行測試，確認全部通過

### 3.3 🔵 重構 - 清理命名一致性
- [x] 檢查並移除 `backend/models/task.py` 中未使用的 `func` import
- [x] 檢查並移除 `backend/services/path_service.py`（原 pathService.py）中未使用的 `os` import
- [x] 全域搜尋確認無殘留的舊命名引用
- [x] 執行測試，確認仍然通過

## 4. 統一依賴注入模式（Preview 路由）

### 4.1 🔴 紅燈 - 撰寫 Preview 路由依賴注入測試
- [x] 在 `tests/backend/test_preview_service.py` 新增測試：透過 FastAPI TestClient 呼叫 preview 端點，驗證 Service 透過 Depends 注入
- [x] 執行測試，確認失敗

### 4.2 🟢 綠燈 - 重構 Preview 路由注入方式
- [x] 在 `backend/dependencies.py` 新增 `depends_preview_service` 函式
- [x] 修改 `backend/routers/preview.py`，將直接實例化改為 `Depends(depends_preview_service)`
- [x] 執行測試，確認全部通過

### 4.3 🔵 重構 - 優化依賴注入程式碼
- [x] 檢查所有 routers/ 檔案，確認無其他直接實例化 Service 的情況
- [x] 執行測試，確認仍然通過

## 5. Worker 全域狀態重構

### 5.1 🔴 紅燈 - 撰寫 Worker 依賴注入測試
- [x] 在 `tests/backend/test_worker.py` 新增測試：`process_completed_download` 接收服務依賴作為參數
- [x] 新增測試：確認模組中不存在 `global` 變數宣告
- [x] 執行測試，確認失敗

### 5.2 🟢 綠燈 - 重構 Worker 服務管理
- [x] 修改 `process_completed_download` 函式簽名，新增服務依賴參數
- [x] 移除 `_worker_services` 全域變數與 `get_worker_services()`、`reset_worker_services()` 函式
- [x] 更新 `backend/backend.py` 或 webhook 路由中的 Worker 呼叫方式
- [x] 執行測試，確認全部通過

### 5.3 🔵 重構 - 優化 Worker 程式碼
- [x] 為 `process_completed_download` 補充 docstring（含 Why 說明）
- [x] 檢查 Worker 中的長方法（>30 行），拆分為更小的函式
- [x] 執行測試，確認仍然通過

## 6. PathService 與 SettingService 拆分（SRP）

### 6.1 🔴 紅燈 - 撰寫拆分後的單元測試
- [x] 在 `tests/backend/` 新增 `test_directory_service.py`，測試目錄掃描功能
- [x] 在 `tests/backend/` 新增 `test_path_validator.py`，測試路徑驗證功能
- [x] 修改 `tests/backend/test_setting_service.py`，移除驗證相關測試（改由 path_validator 測試覆蓋）
- [x] 執行測試，確認新測試失敗

### 6.2 🟢 綠燈 - 實作拆分
- [x] 建立 `backend/utils/path_validator.py`，包含 `validate_path_access()` 與 `is_absolute_path()` 函式
- [x] 將 `backend/services/path_service.py` 重新命名為 `backend/services/directory_service.py`，僅保留目錄掃描邏輯
- [x] 修改 `backend/services/setting_service.py`，將目錄驗證邏輯委派給 `path_validator`
- [x] 更新 `backend/dependencies.py` 與 `backend/routers/directory.py` 的注入邏輯
- [x] 執行測試，確認全部通過

### 6.3 🔵 重構 - 優化拆分後的程式碼
- [x] 為 `DirectoryService` 和 `PathValidator` 補充 docstring
- [x] 確認 `SettingService` 方法數 ≤ 10
- [x] 執行測試，確認仍然通過

## 7. Backend 型別提示補齊

### 7.1 🔴 紅燈 - 撰寫型別完整性驗證
- [x] 使用 `mypy` 或手動檢查 `backend/services/log_service.py`、`backend/repositories/` 中缺少回傳型別的函式
- [x] 記錄所有需補齊的函式清單

### 7.2 🟢 綠燈 - 補齊型別提示
- [x] 為 `log_service.py` 的 `get_logs_by_task_id` 和 `create_log` 補上回傳型別
- [x] 為 `repositories/setting.py` 的 `update_many` 改善參數型別（使用更具體的型別定義）
- [x] 掃描並補齊所有 `backend/` 中缺少回傳型別的公開方法
- [x] 執行測試，確認全部通過

### 7.3 🔵 重構 - 型別一致性檢查
- [x] 確認所有 Pydantic schema 的欄位都有明確的型別標註
- [x] 消除所有 magic number，改用具名常數
- [x] 執行測試，確認仍然通過

## 8. Frontend TaskDetailView 拆分

### 8.1 🔴 紅燈 - 撰寫子元件測試
- [x] 在 `src/components/__tests__/` 新增 `TaskEditForm.spec.ts`，測試表單編輯邏輯
- [x] 在 `src/components/__tests__/` 新增 `TaskLogsPanel.spec.ts`，測試日誌顯示與重新載入
- [x] 在 `src/components/__tests__/` 新增 `TaskDeleteDialog.spec.ts`，測試刪除確認流程
- [x] 執行測試，確認失敗（元件尚未建立）

### 8.2 🟢 綠燈 - 建立子元件
- [x] 建立 `src/components/TaskEditForm.vue`，從 TaskDetailView 提取表單邏輯與模板
- [x] 建立 `src/components/TaskLogsPanel.vue`，從 TaskDetailView 提取日誌面板
- [x] 建立 `src/components/TaskDeleteDialog.vue`，從 TaskDetailView 提取刪除對話框
- [x] 重構 `src/views/TaskDetailView.vue` 為協調元件，引用三個子元件
- [x] 確認 TaskDetailView.vue ≤ 200 行
- [x] 執行測試，確認全部通過

### 8.3 🔵 重構 - 優化元件介面
- [x] 確認子元件使用 `v-model` 與 `defineEmits` 保持介面清晰
- [x] 檢查模板巢狀層級 ≤ 5 層
- [x] 執行測試，確認仍然通過

## 9. Frontend 型別安全與命名一致性

### 9.1 🔴 紅燈 - 撰寫型別安全測試
- [x] 在 `src/schemas/__tests__/` 新增 `errors.spec.ts`，測試 `ApiError` 類別行為
- [x] 執行測試，確認失敗

### 9.2 🟢 綠燈 - 實作型別安全改進
- [x] 建立 `src/schemas/errors.ts`，定義 `ApiError` 類別與 `ApiErrorDetail` 介面
- [x] 修改 `src/composables/useHttpService.ts`，統一拋出 `ApiError`
- [x] 建立 `ToastOptions` 介面，取代 `src/composables/useNotification.ts` 中的 `Record<string, any>`
- [x] 更新所有使用 `as Error` 或 `as { error?: string }` 的元件，改用 `ApiError` 型別守衛
- [x] 執行測試，確認全部通過

### 9.3 🔵 重構 - 統一命名慣例
- [x] 將所有事件處理器重新命名為 `handle*` 前綴（`btnActionUpdateTask` → `handleUpdateTask`、`onDirectorySelected` → `handleDirectorySelect`）
- [x] 修正 `SidebarItem.vue` 的冗餘命名（`taskName` → `name`、`taskEnabled` → `enabled`）
- [x] 為 Pinia Store（`taskStore.ts`、`settingStore.ts`）補充 JSDoc 文件
- [x] 執行測試，確認仍然通過

## 10. 文件更新與 Docstring 補充

- [x] 10.1 為 Backend 所有 Service 類別補充類別層級 docstring（含 Why 說明）
- [x] 10.2 為 Backend 複雜函式（條件分支 ≥ 3 個）補充方法層級 docstring
- [x] 10.3 為 Frontend Composable 函式補充 JSDoc（`usePreview.ts`、`useException.ts`）
- [x] 10.4 確認所有 `TODO` 標記包含 issue 編號或負責人
- [x] 10.5 移除所有已註解掉的程式碼

## 11. 整合測試與品質檢查

- [x] 11.1 執行完整 Backend 測試套件（`pytest --cov`），確認全部通過且覆蓋率未下降
- [x] 11.2 執行完整 Frontend 測試套件（`vitest run --coverage`），確認全部通過
- [x] 11.3 執行 TypeScript 編譯檢查（`vue-tsc -b`），確認無型別錯誤
- [x] 11.4 執行 Frontend 建置（`vite build`），確認產出正常
- [ ] 11.5 手動驗證主要功能流程：建立任務、編輯任務、刪除任務、webhook 觸發檔案移動
