## 1. 前置準備

- [x] 1.1 在 `backend/schemas.py` 建立批量 request/response schemas 的型別骨架（空定義，僅放 `pass`），供後續測試 import
- [x] 1.2 在 `backend/repositories/task.py` 建立 `batch_create` / `batch_update` / `batch_delete` 方法骨架（`raise NotImplementedError`）
- [x] 1.3 在 `backend/services/task_service.py` 建立對應批量方法骨架（`raise NotImplementedError`）
- [x] 1.4 在 `backend/routers/task.py` 註冊 `POST|PUT|DELETE /api/v1/tasks/batch` 路由骨架（回傳 `501`）
- [x] 1.5 在 `src/schemas/` 建立批量請求/回應的 zod schema 骨架
- [x] 1.6 在 `src/stores/taskStore.ts` 保留既有 `batchDelete` / `batchEnable` / `batchDisable` / `batchSetEnabled` 介面，標記為待改寫

## 2. 後端 Repository 批量建立

### 2.1 🔴 紅燈 - 撰寫批量建立 repository 測試
- [x] 2.1.1 在 `tests/backend/repositories/test_task_repository.py` 新增測試：成功建立多筆，DB 內可查得
- [x] 2.1.2 新增測試：批量中某筆 `name` 與 DB 現有重複，拋出 `TaskAlreadyExists`，整體未寫入（session rollback）
- [x] 2.1.3 新增測試：批量內部兩筆同名，拋出 `TaskAlreadyExists`（intra-batch），整體未寫入
- [x] 2.1.4 執行測試，確認全部失敗

### 2.2 🟢 綠燈 - 實作 `TaskRepository.batch_create`
- [x] 2.2.1 實作 `batch_create(items: list[TaskCreate]) -> list[models.Task]`：一次 session，逐筆 `add`，檢查 intra-batch 重名與 DB 重名，統一 `commit`；例外時 `rollback`
- [x] 2.2.2 執行測試，確認全部通過

### 2.3 🔵 重構 - 優化批量建立
- [x] 2.3.1 抽出「名稱衝突檢查」輔助函式
- [x] 2.3.2 執行測試，確認仍通過

## 3. 後端 Repository 批量更新

### 3.1 🔴 紅燈 - 撰寫批量更新 repository 測試
- [x] 3.1.1 測試：批量更新 3 筆 `enabled=False`，DB 中 3 筆 enabled 皆為 False
- [x] 3.1.2 測試：其中一筆 `id` 不存在，拋出 `TaskNotFound`，整體未更新（rollback）
- [x] 3.1.3 測試：兩筆 patch 欲改同名，拋出 `TaskAlreadyExists`，整體未更新
- [x] 3.1.4 測試：patch 僅含部分欄位（`exclude_unset`）時，其他欄位不變
- [x] 3.1.5 執行測試，確認全部失敗

### 3.2 🟢 綠燈 - 實作 `TaskRepository.batch_update`
- [x] 3.2.1 實作 `batch_update(items: list[TaskBatchUpdateItem]) -> list[models.Task]`：單一 session，逐筆 `get_by_id`，缺失則拋例外；處理 `tag_ids` 與 partial patch；統一 `commit`；例外時 `rollback`
- [x] 3.2.2 執行測試，確認全部通過

### 3.3 🔵 重構 - 優化批量更新
- [x] 3.3.1 抽出「單筆 patch 套用」輔助函式
- [x] 3.3.2 執行測試，確認仍通過

## 4. 後端 Repository 批量刪除

### 4.1 🔴 紅燈 - 撰寫批量刪除 repository 測試
- [x] 4.1.1 測試：批量刪除存在的 3 筆，DB 中該 3 筆被移除
- [x] 4.1.2 測試：`ids` 含不存在 id，拋出 `TaskNotFound`，整體未刪除（rollback）
- [x] 4.1.3 測試：`ids` 為空，repository 拒絕（或由 service 層拒絕——擇一即可，於此確認行為）
- [x] 4.1.4 執行測試，確認全部失敗

### 4.2 🟢 綠燈 - 實作 `TaskRepository.batch_delete`
- [x] 4.2.1 實作 `batch_delete(ids: list[str]) -> list[str]`：單一 session，先 `get` 驗證全部存在，再逐筆 `delete`，統一 `commit`；例外時 `rollback`
- [x] 4.2.2 執行測試，確認全部通過

### 4.3 🔵 重構 - 優化批量刪除
- [x] 4.3.1 以一次 `IN` 查詢取代 N 次 `get_by_id` 以驗證存在性
- [x] 4.3.2 執行測試，確認仍通過

## 5. 後端 Service 批量方法

### 5.1 🔴 紅燈 - 撰寫批量 service 測試
- [x] 5.1.1 `test_task_service.py` 測試：`batch_create_tasks` 委派至 repository 並回傳結果
- [x] 5.1.2 測試：`batch_update_tasks` 對於 patch 中的 `name` 執行與現有資料的衝突檢查
- [x] 5.1.3 測試：`batch_delete_tasks` 委派至 repository
- [x] 5.1.4 測試：三個方法遇到例外時正確往上拋（讓 router 轉 HTTP 錯誤）
- [x] 5.1.5 執行測試，確認全部失敗

### 5.2 🟢 綠燈 - 實作 Service 批量方法
- [x] 5.2.1 實作 `TaskService.batch_create_tasks`
- [x] 5.2.2 實作 `TaskService.batch_update_tasks`（含 intra-batch 與 DB 既有 name 衝突檢查）
- [x] 5.2.3 實作 `TaskService.batch_delete_tasks`
- [x] 5.2.4 執行測試，確認全部通過

### 5.3 🔵 重構 - 整理 Service 層
- [x] 5.3.1 抽出共用的 `name` 衝突檢查至私有方法
- [x] 5.3.2 執行測試，確認仍通過

## 6. 後端 Schemas 與 Router

### 6.1 🔴 紅燈 - 撰寫 Schemas 與 Router 測試
- [x] 6.1.1 `test_schemas.py` 測試：`TaskBatchCreate` / `TaskBatchUpdate` / `TaskBatchDelete` / `TaskBatchResult` 之欄位、預設值、長度上限驗證
- [x] 6.1.2 `test_task_router.py` 測試 `POST /api/v1/tasks/batch`：成功、重名衝突、超量
- [x] 6.1.3 `test_task_router.py` 測試 `PUT /api/v1/tasks/batch`：成功批量 `enabled=False`、id 不存在、intra-batch 名稱衝突
- [x] 6.1.4 `test_task_router.py` 測試 `DELETE /api/v1/tasks/batch`：成功、id 不存在、空陣列
- [x] 6.1.5 執行測試，確認全部失敗

### 6.2 🟢 綠燈 - 實作 Schemas 與 Router
- [x] 6.2.1 於 `backend/schemas.py` 完成 `TaskBatchCreate`、`TaskBatchUpdateItem`、`TaskBatchUpdate`、`TaskBatchDelete`、`TaskBatchResult`，含 `items`/`ids` 長度上限（例如 500）
- [x] 6.2.2 於 `backend/routers/task.py` 將 batch 路由骨架替換為呼叫 service 的實作
- [x] 6.2.3 將 service / repository 例外對應為 HTTP 400 / 404（於 `backend/exceptions/` 或 router 局部處理）
- [x] 6.2.4 執行測試，確認全部通過

### 6.3 🔵 重構 - 整理 Router
- [x] 6.3.1 依既有風格抽離 response_model 與 summary 註解
- [x] 6.3.2 確認 OpenAPI 文件 (`/docs`) 顯示三個 batch 端點與正確的 schema
- [x] 6.3.3 執行測試，確認仍通過

## 7. 前端 Store 批量方法重寫

### 7.1 🔴 紅燈 - 撰寫 taskStore 批量測試
- [x] 7.1.1 在 `src/stores/__tests__/taskStore.spec.ts` 撰寫：`batchDelete` 只呼叫 `request` 一次，method/url/body 符合契約
- [x] 7.1.2 撰寫：`batchEnable` / `batchDisable` 只呼叫 `request` 一次，body `items` 內容正確
- [x] 7.1.3 撰寫：API 成功後本地 `tasks` 依 response 更新，`selectedTaskIds` 清空
- [x] 7.1.4 撰寫：API 失敗時 `tasks` 與 `selectedTaskIds` 不變，`error` 被設定
- [x] 7.1.5 執行測試，確認全部失敗

### 7.2 🟢 綠燈 - 重寫 taskStore 批量方法
- [x] 7.2.1 新增 zod schemas（`TaskBatchDeleteRequest`、`TaskBatchUpdateRequest`、`TaskBatchResult`）於 `src/schemas/`
- [x] 7.2.2 重寫 `batchDelete` 為一次 `DELETE /api/v1/tasks/batch`；成功後依 `deleted_ids` 移除本地 tasks
- [x] 7.2.3 重寫 `batchSetEnabled`（連動 `batchEnable` / `batchDisable`）為一次 `PUT /api/v1/tasks/batch`；成功後依回傳 items 以 id 更新本地 tasks
- [x] 7.2.4 執行測試，確認全部通過

### 7.3 🔵 重構 - 抽離共用邏輯
- [x] 7.3.1 抽離「以回傳 items 覆蓋本地 tasks」為私有 helper
- [x] 7.3.2 執行測試，確認仍通過

## 8. 前端 SelectionBar 整合

### 8.1 🔴 紅燈 - 撰寫 SelectionBar 行為測試
- [x] 8.1.1 在 selection-bar 元件的 `__tests__` 中撰寫：點擊「刪除」時呼叫 `taskStore.batchDelete` 一次；按鈕 loading 狀態正確
- [x] 8.1.2 撰寫：點擊「啟用」/「停用」時呼叫對應 store 方法一次；錯誤發生時保留選取
- [x] 8.1.3 執行測試，確認全部失敗

### 8.2 🟢 綠燈 - 調整 SelectionBar 元件
- [x] 8.2.1 確認元件呼叫 store 的 `batchEnable` / `batchDisable` / `batchDelete`，loading/error 與單次請求對齊
- [x] 8.2.2 執行測試，確認全部通過

### 8.3 🔵 重構 - 清理元件
- [x] 8.3.1 移除舊的逐筆迴圈殘留邏輯與註解
- [x] 8.3.2 執行測試，確認仍通過

## 9. 整合測試

- [x] 9.1 後端：撰寫 `tests/backend/test_tasks_batch_flow.py`，以 FastAPI TestClient 覆蓋三個批量端點的完整流程（建立 → 更新 → 刪除）
- [ ] 9.2 前端：以 MCP Chrome DevTools 手動/自動驗證，於 `TasksListView` 多選數筆任務後分別執行啟用、停用、刪除，透過 Network 面板確認僅送出 1 次 `/api/v1/tasks/batch` 請求，且畫面與 DB 狀態一致（待手動驗證）
- [x] 9.3 確認既有 `src/stores/__tests__/taskStore.spec.ts`、`SidebarTool.spec.ts` 等受影響測試全部通過

## 10. 文件更新

- [x] 10.1 更新後端 `README` 或 API 文件段落說明新增的 batch 端點（專案無專屬 README，改由 FastAPI OpenAPI 自動產生文件承擔）
- [x] 10.2 若 `CLAUDE.md` 記載了可用端點或前端批量行為，同步更新（專案無 `CLAUDE.md`）
- [x] 10.3 確認 `/docs`（FastAPI OpenAPI）正確呈現三個 batch 端點的 request/response schema

## 11. 程式碼品質檢查

- [x] 11.1 後端：執行 `pytest` 全部通過（352 passed, 1 skipped，含新增 74 筆批量相關測試）
- [x] 11.2 後端：執行 ruff 確認本次新增/修改的程式碼無 lint 錯誤（既有不相關錯誤不處理）
- [x] 11.3 前端：執行 `vue-tsc --noEmit` 確認型別通過
- [x] 11.4 前端：執行 `vitest run` 全部通過（12 test files, 104 tests passed）
- [ ] 11.5 以繁體中文撰寫 commit message（例：`feat: 新增批量任務 CRUD API 與前端單次呼叫整合`）— 由使用者執行 `/commit` 時完成
