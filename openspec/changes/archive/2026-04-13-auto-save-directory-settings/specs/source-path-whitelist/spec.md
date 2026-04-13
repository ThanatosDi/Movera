## MODIFIED Requirements

### Requirement: 設定頁面 SHALL 提供檔案來源白名單管理 UI

設定頁面 SHALL 包含一個獨立的 card 區塊，讓使用者管理 `allowed_source_directories` 白名單。新增和刪除操作 SHALL 立即透過 API 保存並顯示通知。來自環境變數的項目 SHALL 顯示鎖頭圖示且不可刪除。當 `ALLOW_WEBUI_SETTING=false` 時，新增輸入框 SHALL 被隱藏。

#### Scenario: 新增來源目錄後立即保存
- **WHEN** 使用者在輸入框中輸入有效的絕對路徑並點擊新增按鈕或按 Enter
- **THEN** 系統 SHALL 立即透過 API 保存變更，並顯示成功通知

#### Scenario: 新增失敗時顯示錯誤通知
- **WHEN** 使用者新增路徑後 API 保存失敗
- **THEN** 系統 SHALL 顯示錯誤通知，並將本地狀態回滾至操作前

#### Scenario: 輸入無效路徑時顯示錯誤
- **WHEN** 使用者在輸入框中輸入非絕對路徑
- **THEN** 系統 SHALL 顯示錯誤提示，且不將該路徑加入列表

#### Scenario: 移除資料庫來源的目錄後立即保存
- **WHEN** 使用者點擊某個 `source` 為 `"db"` 的來源目錄項目旁的移除按鈕
- **THEN** 系統 SHALL 立即透過 API 保存變更，並顯示成功通知

#### Scenario: 移除失敗時顯示錯誤通知並回滾
- **WHEN** 使用者移除路徑後 API 保存失敗
- **THEN** 系統 SHALL 顯示錯誤通知，並將該路徑恢復至列表中

#### Scenario: 環境變數項目不可移除
- **WHEN** 某個來源目錄項目的 `source` 為 `"env"`
- **THEN** UI SHALL 顯示鎖頭圖示，不顯示移除按鈕

#### Scenario: ALLOW_WEBUI_SETTING=false 時隱藏新增功能
- **WHEN** `ALLOW_WEBUI_SETTING=false`
- **THEN** UI SHALL 隱藏新增輸入框，僅顯示現有清單（唯讀）

#### Scenario: 白名單為空時顯示安全提示
- **WHEN** `allowed_source_directories` 白名單為空
- **THEN** UI SHALL 顯示提示文字，提醒使用者設定白名單以增強安全性
