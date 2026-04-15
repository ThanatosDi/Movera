### Requirement: 批量建立任務 API
系統 SHALL 提供 `POST /api/v1/tasks/batch` 端點，接受 `{ "items": TaskCreate[] }` 形式的請求，於單一資料庫交易中建立多筆任務。任一筆驗證或唯一性檢查失敗時，整筆請求 SHALL 回滾，並回傳包含失敗項資訊的 4xx 錯誤。

#### Scenario: 全部成功建立
- **WHEN** 客戶端以 `POST /api/v1/tasks/batch` 送出 3 筆有效且名稱互不相同、與 DB 無衝突的 `TaskCreate`
- **THEN** 系統 SHALL 回應 HTTP 201，response body `items` 包含 3 筆完整的 `Task`（含 `id`、`created_at` 等），且資料庫中該 3 筆任務皆已建立

#### Scenario: 其中一筆與現有任務重名
- **WHEN** 批量建立的 `items` 中存在某筆 `name` 已於資料庫中存在
- **THEN** 系統 SHALL 回應 HTTP 400（或 409），並在 `detail` 欄位中指出衝突的 `name`，資料庫中 SHALL 不新增任何任務

#### Scenario: 批量內部有重名
- **WHEN** 批量 `items` 內自身有兩筆 `name` 相同
- **THEN** 系統 SHALL 在寫入前拒絕，回應 HTTP 400，並指出重複的 `name`

#### Scenario: 超過批量筆數上限
- **WHEN** 客戶端送出的 `items` 數量超過系統設定的批量上限（例如 500）
- **THEN** 系統 SHALL 回應 HTTP 400，`detail` 說明超量

### Requirement: 批量更新任務 API
系統 SHALL 提供 `PUT /api/v1/tasks/batch` 端點，接受 `{ "items": [{ "id": str, "patch": TaskUpdatePartial }, ...] }` 形式的請求，於單一資料庫交易中更新多筆任務。任一筆的 ID 不存在或欄位驗證失敗時，整筆請求 SHALL 回滾。

#### Scenario: 批量啟用 / 停用成功
- **WHEN** 客戶端送出 `items: [{id, patch: {enabled: false}}, ...]` 共 5 筆皆為已存在的 task id
- **THEN** 系統 SHALL 回應 HTTP 200，response body `items` 包含 5 筆更新後的完整 `Task`；資料庫中該 5 筆 `enabled` 皆被更新為 `false`

#### Scenario: 其中一筆 ID 不存在
- **WHEN** 批量 `items` 中任一筆 `id` 在資料庫中不存在
- **THEN** 系統 SHALL 回應 HTTP 404，`detail` 指出缺失的 `id`，且其他筆 SHALL 不被更新（交易回滾）

#### Scenario: 批量內部欄位造成名稱衝突
- **WHEN** 批量 `items` 欲將兩筆不同任務更新為同一 `name`
- **THEN** 系統 SHALL 回應 HTTP 400，`detail` 指出衝突的 `name`，且 SHALL 不變動任何任務

### Requirement: 批量刪除任務 API
系統 SHALL 提供 `DELETE /api/v1/tasks/batch` 端點，接受 `{ "ids": str[] }` 形式的 request body，於單一資料庫交易中刪除多筆任務。任一 ID 不存在時，整筆請求 SHALL 回滾。

#### Scenario: 全部成功刪除
- **WHEN** 客戶端以 `DELETE /api/v1/tasks/batch` 送出 `{ "ids": [...] }`，所有 id 皆存在
- **THEN** 系統 SHALL 回應 HTTP 200，response body `deleted_ids` 等於請求的 `ids`，資料庫中該些任務 SHALL 被刪除

#### Scenario: 其中一筆 ID 不存在
- **WHEN** `ids` 中含有不存在的任務 id
- **THEN** 系統 SHALL 回應 HTTP 404，`detail` 指出缺失的 id，且 SHALL 不刪除任何任務

#### Scenario: 空陣列請求
- **WHEN** `ids` 為空陣列
- **THEN** 系統 SHALL 回應 HTTP 400，`detail` 說明需至少 1 筆 id

### Requirement: 批量 API 交易原子性
所有批量端點（`POST|PUT|DELETE /api/v1/tasks/batch`）SHALL 於單一資料庫交易內處理，確保「全部成功或全部回滾」的原子性，並於錯誤時保持資料庫狀態不變。

#### Scenario: Repository 層例外觸發整體回滾
- **WHEN** 批量處理中途任一 ORM 操作拋出例外
- **THEN** 系統 SHALL rollback 交易，使資料庫中受批量影響的任務維持原狀；HTTP 回應為對應的 4xx / 5xx

### Requirement: 前端批量操作以單次請求完成
前端 `taskStore` 的 `batchDelete`、`batchEnable`、`batchDisable`、`batchSetEnabled` SHALL 僅對後端發出一次 HTTP 請求；操作成功後 SHALL 以回應內容原子更新本地 `tasks` 清單並清空 `selectedTaskIds`。

#### Scenario: batchDelete 只打一次 API
- **WHEN** 使用者選取 5 筆任務並呼叫 `batchDelete`
- **THEN** `request` SHALL 只被呼叫 1 次，`method` 為 `DELETE`、`url` 為 `/api/v1/tasks/batch`，`body.ids` 等於 5 筆任務的 id；成功後本地 `tasks` SHALL 已移除該 5 筆，且 `selectedTaskIds` SHALL 為空

#### Scenario: batchSetEnabled 只打一次 API
- **WHEN** 使用者選取 3 筆任務並呼叫 `batchSetEnabled(false)`
- **THEN** `request` SHALL 只被呼叫 1 次，`method` 為 `PUT`、`url` 為 `/api/v1/tasks/batch`，`body.items` 每筆為 `{id, patch: {enabled: false}}`；成功後本地對應的 task `enabled` SHALL 皆為 `false`

#### Scenario: 批量 API 失敗時不修改本地狀態
- **WHEN** 呼叫 `batchDelete` 後 API 回應非 2xx
- **THEN** store 的 `tasks` SHALL 維持原樣，`error` SHALL 被設定，`selectedTaskIds` SHALL 維持原樣，使用者可重試
