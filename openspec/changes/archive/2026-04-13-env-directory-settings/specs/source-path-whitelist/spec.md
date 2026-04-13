## MODIFIED Requirements

### Requirement: 設定頁面 SHALL 提供檔案來源白名單管理 UI

設定頁面 SHALL 包含一個獨立的 card 區塊，讓使用者管理 `allowed_source_directories` 白名單。UI 操作模式 SHALL 與既有的 `allowed_directories`（目錄選擇器允許清單）一致。來自環境變數的項目 SHALL 顯示鎖頭圖示且不可刪除。當 `ALLOW_WEBUI_SETTING=false` 時，新增輸入框 SHALL 被隱藏。

#### Scenario: 新增來源目錄
- **WHEN** 使用者在輸入框中輸入有效的絕對路徑（如 `/downloads`）並點擊新增按鈕或按 Enter
- **THEN** 該路徑 SHALL 被加入白名單列表中

#### Scenario: 輸入無效路徑時顯示錯誤
- **WHEN** 使用者在輸入框中輸入非絕對路徑（如 `downloads/anime`）
- **THEN** 系統 SHALL 顯示錯誤提示，且不將該路徑加入列表

#### Scenario: 移除資料庫來源的目錄
- **WHEN** 使用者點擊某個 `source` 為 `"db"` 的來源目錄項目旁的移除按鈕
- **THEN** 該路徑 SHALL 從白名單列表中移除

#### Scenario: 環境變數項目不可移除
- **WHEN** 某個來源目錄項目的 `source` 為 `"env"`
- **THEN** UI SHALL 顯示鎖頭圖示，不顯示移除按鈕

#### Scenario: ALLOW_WEBUI_SETTING=false 時隱藏新增功能
- **WHEN** `ALLOW_WEBUI_SETTING=false`
- **THEN** UI SHALL 隱藏新增輸入框，僅顯示現有清單（唯讀）

#### Scenario: 儲存白名單設定
- **WHEN** 使用者修改白名單後點擊「儲存設定」按鈕
- **THEN** 系統 SHALL 透過 `PUT /api/v1/settings` 將 `allowed_source_directories` 連同其他設定一併儲存

#### Scenario: 白名單為空時顯示安全提示
- **WHEN** `allowed_source_directories` 白名單為空（無環境變數項目也無資料庫項目）
- **THEN** UI SHALL 顯示提示文字，提醒使用者設定白名單以增強安全性
