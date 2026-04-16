## Why

目前前端在多選任務後執行批量操作（啟用、停用、刪除）時，會以迴圈方式對每個 task 逐一發送 HTTP 請求（N 次 API 呼叫）。這在選取數量大時造成明顯的效能與使用者體驗問題：網路往返延遲累加、進度無法一次回報、任一請求失敗會讓結果處於不一致狀態。本次變更將批量操作改為「一次 API 呼叫」完成，降低延遲、提升可靠性，並讓後端能以單一交易確保原子性。

## What Changes

- 新增後端批量 API 節點：
  - `POST /api/v1/tasks/batch`：批量建立任務
  - `PUT /api/v1/tasks/batch`：批量更新任務（支援依 ID 差異化更新，以及統一欄位更新例如 `enabled`）
  - `DELETE /api/v1/tasks/batch`：批量刪除任務（以 request body 帶入 ID 清單）
- 新增後端對應的 Pydantic schemas（`TaskBatchCreate`、`TaskBatchUpdate`、`TaskBatchDelete`、`TaskBatchResult`）
- `TaskService` 與 `TaskRepository` 新增批量方法，於單一 DB session 交易中完成（全部成功或全部失敗，並回報個別失敗清單）
- 調整前端 `taskStore` 的 `batchDelete`、`batchEnable`、`batchDisable`、`batchSetEnabled`，改為只呼叫一次批量 API 節點，不再於前端迴圈逐筆請求
- `SelectionBar`（選擇模式操作列）在觸發批量操作時改用新的批量端點；loading 與錯誤處理以單一請求為單位

## Capabilities

### New Capabilities
- `batch-task-operations`: 提供後端批量 CRUD API，以及前端多選操作改為單次 API 呼叫的行為契約

### Modified Capabilities
- `selection-bar`: 批量操作列觸發後的 API 行為由 N 次請求變更為 1 次請求；錯誤/載入狀態語意隨之更新

## Impact

- Backend
  - `backend/routers/task.py`：新增 `/tasks/batch` 三個端點
  - `backend/services/task_service.py`：新增批量方法
  - `backend/repositories/task.py`：新增批量 repository 方法（單一 session commit）
  - `backend/schemas.py`：新增批量 request/response schemas
  - `backend/exceptions/task_exception.py`：可能新增 `TaskBatchPartialFailure` 或重用既有例外
- Frontend
  - `src/stores/taskStore.ts`：重寫 `batchDelete`、`batchEnable`、`batchDisable`、`batchSetEnabled`
  - `src/components/SelectionBar.vue`（或操作列元件）：對應呼叫更新，loading 行為簡化
  - `src/schemas/`：新增批量請求/回應的 zod schema
- Tests
  - 後端：新增 `tests/backend/` 針對批量路由、服務、儲存庫的測試（TDD 紅綠燈流程）
  - 前端：更新 `src/stores/__tests__/taskStore.spec.ts` 的批量操作測試為單次呼叫驗證
- 不影響：單筆 CRUD API（`/tasks/{id}`）仍保留以維持既有功能與詳細頁面使用
