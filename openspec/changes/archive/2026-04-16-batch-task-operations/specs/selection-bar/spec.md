## ADDED Requirements

### Requirement: 批量操作列透過單次批量 API 執行操作
當使用者於選擇模式中觸發批量操作（啟用、停用、刪除）時，前端 SHALL 對後端發出**單次**批量 API 請求（`/api/v1/tasks/batch`），不再對選取的每筆任務迴圈發送請求。

#### Scenario: 點擊批量刪除僅發出一次請求
- **WHEN** 使用者已選取 N 筆任務並點擊「刪除」按鈕（N ≥ 1）
- **THEN** 系統 SHALL 僅發出 1 次 HTTP 請求至 `DELETE /api/v1/tasks/batch`，不論 N 的大小

#### Scenario: 點擊批量啟用僅發出一次請求
- **WHEN** 使用者已選取 N 筆任務並點擊「啟用」按鈕
- **THEN** 系統 SHALL 僅發出 1 次 HTTP 請求至 `PUT /api/v1/tasks/batch`，`body.items` 每筆為 `{id, patch: {enabled: true}}`

#### Scenario: 點擊批量停用僅發出一次請求
- **WHEN** 使用者已選取 N 筆任務並點擊「停用」按鈕
- **THEN** 系統 SHALL 僅發出 1 次 HTTP 請求至 `PUT /api/v1/tasks/batch`，`body.items` 每筆為 `{id, patch: {enabled: false}}`

### Requirement: 批量操作期間的載入與錯誤狀態
批量操作進行期間，操作列 SHALL 顯示單次請求對應的 loading 狀態；請求失敗時，SHALL 顯示錯誤訊息並保留使用者的選取狀態以便重試。

#### Scenario: 請求進行中按鈕禁用
- **WHEN** 批量操作 API 請求已送出但尚未回應
- **THEN** 啟用、停用、刪除三個批量操作按鈕 SHALL 為 disabled 狀態，直到請求完成

#### Scenario: 請求失敗保留選取
- **WHEN** 批量操作 API 回應非 2xx
- **THEN** 操作列 SHALL 顯示錯誤訊息，`selectedTaskIds` SHALL 維持原樣，使用者 SHALL 能再次點擊該按鈕重試

#### Scenario: 請求成功後清空選取並離開選擇模式（若原已啟用）
- **WHEN** 批量操作 API 回應 2xx
- **THEN** `selectedTaskIds` SHALL 被清空；若該操作為「刪除」且產品行為要求，`isSelectMode` 的處理 SHALL 與原有刪除流程一致（不因批量化而變更）
