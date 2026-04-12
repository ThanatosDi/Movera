## ADDED Requirements

### Requirement: Regex 編譯與執行超時限制
所有使用者提供的 regex pattern 在編譯與執行時 SHALL 加入超時限制（2 秒）。超時時 SHALL 引發明確的錯誤，而非讓 worker thread 無限掛起。

#### Scenario: 正常 regex pattern 在限時內完成
- **WHEN** 使用者提供 regex pattern `(\d+)` 並搭配一般檔名
- **THEN** 系統 SHALL 在超時限制內正常完成比對並回傳結果

#### Scenario: 惡意 regex pattern 觸發超時
- **WHEN** 使用者提供會導致災難性回溯的 regex pattern（如 `(a+)+$`）搭配惡意輸入
- **THEN** 系統 SHALL 在 2 秒後超時，回傳明確的錯誤訊息而非掛起

### Requirement: Preview API Regex 超時處理
`POST /api/v1/preview/regex` 端點 SHALL 在 regex 超時時回傳 HTTP 422 錯誤，body 包含明確的超時錯誤訊息。

#### Scenario: Preview regex 超時回傳 422
- **WHEN** 使用者在 preview API 提供會超時的 regex pattern
- **THEN** 系統 SHALL 回傳 HTTP 422，body 包含 regex 超時相關的錯誤訊息

### Requirement: Worker Regex 超時處理
Worker 在執行 rename 操作時 SHALL 捕捉 regex 超時錯誤，記錄錯誤日誌並跳過該檔案的重新命名，不影響其他檔案的處理。

#### Scenario: Worker rename regex 超時
- **WHEN** 已儲存的 regex rename rule 在 worker 執行時超時
- **THEN** 系統 SHALL 記錄錯誤日誌並跳過該檔案的重新命名，繼續處理下一個檔案
