## ADDED Requirements

### Requirement: 系統 SHALL 提供檔案來源白名單設定

系統 SHALL 支援 `allowed_source_directories` 設定項，儲存為 JSON 陣列格式的絕對路徑清單。此設定用於限制 Webhook 傳入的檔案路徑必須位於白名單目錄範圍內。

#### Scenario: 白名單設定成功儲存
- **WHEN** 使用者透過 `PUT /api/v1/settings` 傳入 `{"allowed_source_directories": ["/downloads", "/media"]}` 
- **THEN** 系統 SHALL 將設定序列化為 JSON 並儲存至資料庫

#### Scenario: 白名單僅接受絕對路徑
- **WHEN** 使用者傳入包含相對路徑的白名單，如 `{"allowed_source_directories": ["downloads/anime"]}`
- **THEN** 系統 SHALL 回傳 400 錯誤，指出無效的路徑

#### Scenario: 讀取白名單設定
- **WHEN** 系統透過 `GET /api/v1/settings` 取得所有設定
- **THEN** `allowed_source_directories` 欄位 SHALL 被反序列化為原生 JSON 陣列回傳

---

### Requirement: Worker SHALL 驗證檔案來源路徑

Worker 在處理 Webhook 傳入的檔案路徑前，SHALL 檢查該路徑是否位於 `allowed_source_directories` 白名單中任一目錄的範圍內（包含子目錄）。驗證 SHALL 使用 resolved 絕對路徑比對，防止路徑穿越攻擊。

#### Scenario: 檔案路徑在白名單範圍內
- **WHEN** 白名單設定為 `["/downloads"]`，且 Webhook 傳入 `filepath = "/downloads/anime/test.mp4"`
- **THEN** Worker SHALL 正常繼續處理該檔案（匹配任務、重新命名、搬移）

#### Scenario: 檔案路徑不在白名單範圍內
- **WHEN** 白名單設定為 `["/downloads"]`，且 Webhook 傳入 `filepath = "/etc/passwd"`
- **THEN** Worker SHALL 拒絕處理該檔案，記錄警告日誌，並直接返回不執行任何檔案操作

#### Scenario: 白名單為空時允許所有路徑
- **WHEN** `allowed_source_directories` 設定為空陣列 `[]` 或未設定
- **THEN** Worker SHALL 不進行路徑驗證，允許所有路徑通過（向後相容）

#### Scenario: 防止路徑穿越攻擊
- **WHEN** 白名單設定為 `["/downloads"]`，且 Webhook 傳入 `filepath = "/downloads/../etc/passwd"`
- **THEN** Worker SHALL 將路徑 resolve 後判斷為 `/etc/passwd`，不在白名單範圍內，拒絕處理

---

### Requirement: 設定頁面 SHALL 提供檔案來源白名單管理 UI

設定頁面 SHALL 包含一個獨立的 card 區塊，讓使用者管理 `allowed_source_directories` 白名單。UI 操作模式 SHALL 與既有的 `allowed_directories`（目錄選擇器允許清單）一致。

#### Scenario: 新增來源目錄
- **WHEN** 使用者在輸入框中輸入有效的絕對路徑（如 `/downloads`）並點擊新增按鈕或按 Enter
- **THEN** 該路徑 SHALL 被加入白名單列表中

#### Scenario: 輸入無效路徑時顯示錯誤
- **WHEN** 使用者在輸入框中輸入非絕對路徑（如 `downloads/anime`）
- **THEN** 系統 SHALL 顯示錯誤提示，且不將該路徑加入列表

#### Scenario: 移除來源目錄
- **WHEN** 使用者點擊某個來源目錄項目旁的移除按鈕
- **THEN** 該路徑 SHALL 從白名單列表中移除

#### Scenario: 儲存白名單設定
- **WHEN** 使用者修改白名單後點擊「儲存設定」按鈕
- **THEN** 系統 SHALL 透過 `PUT /api/v1/settings` 將 `allowed_source_directories` 連同其他設定一併儲存

#### Scenario: 白名單為空時顯示安全提示
- **WHEN** `allowed_source_directories` 白名單為空
- **THEN** UI SHALL 顯示提示文字，提醒使用者設定白名單以增強安全性
