## Context

Movera v1（`h:/VSCode/Python/Movera`）是一個已運行的全端應用，包含 Backend（FastAPI）與 Frontend（Vue 3）。目前架構分層正確，但存在命名不一致、型別安全不足、部分元件/服務違反 SRP 等技術債。本次重構在 Movera.v2 目錄進行，目標是將程式碼提升至 `openspec/specs/project.md` 所定義的規範標準。

**影響層級**：Router / Service / Repository / Model / Component / Store / Utils / Worker

**現況**：
- Backend 共 36 個 Python 檔案，約 1,939 行
- Frontend 共 147 個 Vue/TypeScript 檔案
- 測試覆蓋：Backend 17 個測試檔、Frontend 8 個測試檔

## Goals / Non-Goals

**Goals:**
- 修復已知邏輯 Bug（rename.py 變數作用域）
- 統一 Backend 模組命名為 snake_case（PEP 8）
- 統一 Frontend 事件處理器命名慣例（`handle*` 前綴）
- 所有 Service 使用 `Depends()` 依賴注入
- 重構違反 SRP 的 Service 與 Component
- 補齊型別提示與 JSDoc/docstring 文件
- 消除 `any` 型別與 magic number
- 確保所有現有測試在重構後仍通過

**Non-Goals:**
- 不變更 API 契約（所有端點行為不變）
- 不變更資料庫結構或 migration
- 不引入新功能
- 不重寫 UI 元件庫（shadcn-vue/Reka UI）
- 不變更建置工具或套件管理器
- 不處理 Frontend schema snake_case → camelCase DTO 轉換（涉及 API 契約變更，排除在本次範圍外）

## Decisions

### 決策 1：Backend Service 檔案重新命名策略

**選擇**：一次性批量重新命名所有 Service 檔案

| 檔案 | 舊名 | 新名 |
|------|------|------|
| Service | `taskService.py` | `task_service.py` |
| Service | `settingService.py` | `setting_service.py` |
| Service | `previewService.py` | `preview_service.py` |
| Service | `pathService.py` | `path_service.py` |
| Service | `logService.py` | `log_service.py` |
| Exception | `taskException.py` | `task_exception.py` |
| Exception | `directoryException.py` | `directory_exception.py` |
| Exception | `workerException.py` | `worker_exception.py` |

**影響層級**：Service / Router / Dependencies / Tests

**理由**：漸進式重新命名會造成混合命名風格的過渡期，增加認知負擔。一次性完成確保一致性。

**替代方案**：逐步重新命名（一次一個檔案）—— 拒絕，因為會在過渡期造成不一致。

### 決策 2：PathService 拆分方式

**選擇**：將 `PathService` 拆分為兩個類別

- `DirectoryService`：負責目錄列表與掃描邏輯（`list_directories`、`_scan_directories`、`_has_subdirectories`）
- `PathValidator`：負責路徑安全驗證（`_validate_path_access`），移至 `utils/` 作為獨立工具函式

**影響層級**：Service / Router（directory.py）/ Dependencies

**理由**：`PathService` 同時處理目錄掃描與安全驗證，違反 SRP。驗證邏輯是通用的，適合作為工具函式。

**替代方案**：保持原樣僅加註解 —— 拒絕，不符合 SRP 規範。

### 決策 3：SettingService 職責分離

**選擇**：將目錄驗證邏輯提取到 `PathValidator`（與決策 2 合併），SettingService 保留 CRUD 與序列化職責

**影響層級**：Service

**理由**：驗證邏輯與設定 CRUD 是不同關注點。JSON 序列化仍與設定管理高度相關，保留在同一 Service 中。

### 決策 4：Worker 全域狀態重構

**選擇**：將 `WorkerServices` 改為函式參數傳入模式，由呼叫端負責建立與管理生命週期

**影響層級**：Worker / Backend（backend.py 啟動邏輯）

**理由**：消除全域可變狀態，提升可測試性與執行緒安全性。

**替代方案**：使用 threading.Lock 保護全域狀態 —— 拒絕，治標不治本。

### 決策 5：Frontend TaskDetailView 拆分

**選擇**：拆分為三個子元件

- `TaskEditForm.vue`：表單編輯邏輯與狀態
- `TaskLogsPanel.vue`：日誌顯示與重新載入
- `TaskDeleteDialog.vue`：刪除確認對話框

**影響層級**：Component / View

**理由**：326 行的單一 View 包含 7 層巢狀，違反 30 行函式限制與 2 層巢狀限制。

### 決策 6：Frontend 型別安全強化

**選擇**：
- 建立 `ApiError` 類別（`src/schemas/errors.ts`）取代 `as` 型別轉換
- 建立 `ToastOptions` 介面取代 `Record<string, any>`
- 在 `useHttpService.ts` 中統一錯誤處理，回傳型別化的 `ApiError`

**影響層級**：Composable / Store / Component

**理由**：型別安全是 TypeScript strict mode 的核心價值，`any` 型別破壞了整個型別鏈。

## Risks / Trade-offs

| 風險 | 緩解措施 |
|------|---------|
| Service 檔案重新命名導致大量 import 路徑失效 | 使用 IDE 全域搜尋替換，完成後立即執行全部測試驗證 |
| Worker 重構可能影響已部署的下載完成回呼 | 保持 `process_completed_download` 函式簽名不變，僅改變內部服務獲取方式 |
| TaskDetailView 拆分可能影響既有的 props/events 傳遞 | 使用 `v-model` 與 `defineEmits` 保持介面一致，新增子元件測試 |
| 大範圍重構可能引入隱性回歸 | 每個重構步驟後執行完整測試套件（Backend: pytest、Frontend: vitest） |
| PathService 拆分後 DirectoryRouter 需要注入兩個依賴 | 僅注入 `DirectoryService`，由其內部呼叫 `PathValidator`，保持 Router 簡潔 |
