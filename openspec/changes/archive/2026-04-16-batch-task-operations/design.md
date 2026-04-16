## Context

目前 Movera 任務 CRUD 僅提供單筆資源端點（`/api/v1/tasks`、`/api/v1/tasks/{task_id}`）。前端於 `src/stores/taskStore.ts` 的 `batchDelete` / `batchSetEnabled` 透過 `for` 迴圈逐筆呼叫這些端點，選取 N 筆則送出 N 次 HTTP 請求。

存在的問題：
- **延遲線性累加**：N 次 round-trip 造成可感知的卡頓，特別是在 selection-bar 顯示 loading 時。
- **缺乏原子性**：任一請求失敗時，部分資料已被修改，無法一次 rollback，前端難以呈現一致狀態。
- **無批量成功/失敗語意**：store 僅能依例外中斷迴圈，未完成的 id 沒有明確回報。
- **DB 多次 commit**：每筆更新觸發一次 SQLAlchemy `commit()`，與 SQLite 的 WAL 行為結合仍屬不必要開銷。

相關檔案：
- Router：[backend/routers/task.py](backend/routers/task.py)
- Service：[backend/services/task_service.py](backend/services/task_service.py)
- Repository：[backend/repositories/task.py](backend/repositories/task.py)
- Schemas：[backend/schemas.py](backend/schemas.py)
- Store：[src/stores/taskStore.ts](src/stores/taskStore.ts)
- Selection Bar：現有 selection-bar 能力位於 [openspec/specs/selection-bar/spec.md](openspec/specs/selection-bar/spec.md)，UI 元件在 `src/components/` 底下由 `TasksListView` 組合使用。

## Goals / Non-Goals

**Goals:**
- 提供批量 CRUD HTTP 端點（Create / Update / Delete），以 JSON body 帶入多筆資料，**單次請求**完成。
- 後端以單一 DB 交易處理批量操作，保證原子性（全部成功或全部回滾），並在回應中回報每筆的處理結果或錯誤。
- 前端 `batchEnable` / `batchDisable` / `batchDelete` 只發出**一次** API 請求，整體 loading / error 狀態以單次請求為單位。
- 保留既有單筆端點不破壞、不改動（非 BREAKING）。

**Non-Goals:**
- **不**改動單筆任務 `/tasks/{task_id}` 的行為與 schema。
- **不**引入背景任務 / 任務佇列 / WebSocket 進度推送。
- **不**支援跨資源（tag + task）的批量操作。
- **不**處理分頁式批量（超大清單）；暫以 request body size 限制 + 單一 transaction 為界（見風險）。

## Decisions

### 決策 1：新增 `/api/v1/tasks/batch` 子路徑而非重用集合端點
- **選擇**：在 Router 新增 `POST|PUT|DELETE /api/v1/tasks/batch` 三個端點。
- **替代方案**：
  - (A) 在 `POST /api/v1/tasks` 同時支援單筆 object 與 list。以 Pydantic `Union` 區分。
  - (B) 使用 RFC 7396 JSON Patch 於既有端點。
- **理由**：
  - (A) 會讓 OpenAPI schema 模糊（單筆 vs 批量 response shape 不同），前端型別推斷變複雜。
  - (B) 屬於 partial update 語意，實作與測試成本高於需求。
  - 子路徑 `/batch` 使 OpenAPI 文件清楚可辨識，前後端契約單純，同時保留日後擴充（如 `/batch?atomic=false`）空間。

### 決策 2：`DELETE` 使用 request body（非 query string）
- **選擇**：`DELETE /api/v1/tasks/batch` 以 JSON body `{ "ids": ["..."] }` 傳遞。
- **替代方案**：`DELETE /api/v1/tasks?ids=a,b,c`（query string）。
- **理由**：
  - ID 為 UUID，數量上限可能達數百；query string 受 URL 長度限制風險較高。
  - FastAPI 支援 `DELETE` 帶 body（RFC 9110 並未禁止）。專案尚未有此用法限制。
  - 與 `POST /batch` 的 body shape 一致，便於前端組合共用型別。

### 決策 3：批量 Update 採「部分欄位統一更新」+「逐筆差異化更新」雙模式
- **選擇**：`PUT /api/v1/tasks/batch` 的 request body 定義如下：
  ```json
  {
    "items": [
      { "id": "uuid-1", "patch": { "enabled": false } },
      { "id": "uuid-2", "patch": { "enabled": false } }
    ]
  }
  ```
  `patch` 為 `TaskUpdate` 的部分欄位（允許 `exclude_unset` 語意）。
- **替代方案**：
  - (A) 定義 `{"ids": [...], "patch": {...}}` 統一套用同一 patch。
  - (B) 僅接受完整 `TaskUpdate` 覆寫（等同 PUT 語意）。
- **理由**：
  - (A) 無法滿足未來「一次更新不同任務的不同欄位」需求，且目前 selection-bar 的 enable / disable 已可由此 shape 表達。
  - (B) 強迫前端從 `taskStore` 組出完整 payload，在 `batchSetEnabled` 只想改 `enabled` 時成本過高。
  - 選定 shape 同時涵蓋「統一 `enabled: true/false`」與未來可能的差異化更新，不新增語意負擔。

### 決策 4：單一交易、Fail-fast + 回報結果
- **選擇**：Repository 新增 `batch_create` / `batch_update` / `batch_delete`；全部在同一 `Session` 中操作，使用 `flush` 收集錯誤，最後一次 `commit`；若任一筆觸發 `TaskNotFound` / `TaskAlreadyExists`，整筆交易 `rollback` 並回傳 HTTP 400 / 404（視例外類型），response body 帶上失敗項的 `id` 與 `reason`。
- **替代方案**：「盡力而為」模式，部分成功也提交，response 回報 `succeeded` 與 `failed` 清單。
- **理由**：
  - 原子性更符合使用者對「一次操作」的直覺（要就全做，不然保持原狀）。
  - 雙模式會讓 schema 與錯誤處理複雜度大增，且目前 selection-bar 的使用情境不需要 partial success。
  - 若日後需要，`POST|PUT|DELETE /batch?atomic=false` 可以用 query flag 擴充，不變動現有契約。

### 決策 5：Response shape 使用 `TaskBatchResult`
- **選擇**：
  ```python
  class TaskBatchResult(BaseModel):
      items: list[Task]      # 成功處理後的完整 Task 物件（create / update）
      deleted_ids: list[str] # 僅 delete 使用；create / update 不填或省略
  ```
  以 HTTP 200（update / delete）或 201（create）回覆。錯誤以 4xx + `detail` 清單回報。
- **理由**：讓前端一次取得最新 Task 資料並覆蓋 store，避免二次 `fetchTasks`。

### 決策 6：前端 store 直接呼叫批量端點並原子更新本地狀態
- **選擇**：
  - `batchDelete` → `DELETE /tasks/batch` 一次呼叫；成功後依回傳的 `deleted_ids` 自本地 `tasks` 陣列移除並清空 `selectedTaskIds`。
  - `batchSetEnabled(enabled)` → `PUT /tasks/batch` 一次呼叫，`items` 由 `selectedTaskIds` 產生 `{id, patch: { enabled }}`；成功後依回傳 `items` 以 `id` 找到本地 task 物件替換。
  - 失敗時整體 rollback 觀感：不修改本地 `tasks`，僅設定 `error`。
- **替代方案**：樂觀更新本地狀態、失敗再回復。
- **理由**：批量操作耗時短（單一請求），樂觀更新複雜度與收益不成比例；一致性優先。

### 決策 7：TDD 紅綠燈循環
- 實作順序依專案規範先寫測試：
  - 🔴 Backend: 針對 router、service、repository 的批量路徑撰寫 pytest 測試，確認 red
  - 🟢 實作最小程式碼讓測試通過
  - 🔵 重構
  - 前端同樣先以 Vitest 寫 `taskStore.spec.ts` 中的 batch 行為（mock `request`）的紅燈測試

## Risks / Trade-offs

- **DELETE 帶 body 的代理相容性** → 大多數反向代理（nginx、Caddy、Traefik）允許 `DELETE` body；若部署環境剝除 body，會造成刪除無效。→ **Mitigation**：若日後出現相容性問題，可追加 `POST /api/v1/tasks/batch/delete` 作為別名。先以標準 `DELETE + body` 作為主要契約並於 OpenAPI 標示。
- **SQLite 單一交易批量寫入可能放大鎖時間** → SQLite 在寫入時會取得 reserved/exclusive lock，若批量筆數極多，會阻塞其他請求短暫時間。→ **Mitigation**：於 schema 層限制 `items` / `ids` 長度上限（如 500），並以 400 拒絕超量請求；日後若需更大可改為分塊處理。
- **API 契約擴散** → 新增 3 個端點會讓 OpenAPI 頁面變長。→ **Mitigation**：以同一 `tags=["Tasks"]` 分組，summary 清楚標明「批量」。
- **前端樂觀更新拿掉後，使用者點擊到結果的感知延遲** → 若批量數量極大，單次 request 仍會慢。→ **Mitigation**：SelectionBar 顯示 loading；若未來需要可再加入進度回饋，不在本次範圍。
- **既有單筆 update 要求 `exclude.name != new.name` 驗證衝突** → 批量情境若兩筆 patch 改成同名，會觸發重複檢查。→ **Mitigation**：service 批量更新在同一次處理中針對 `name` 欄位建立集合，偵測 intra-batch 衝突並回報；與 DB 現有資料衝突則透過既有 query 檢查。
