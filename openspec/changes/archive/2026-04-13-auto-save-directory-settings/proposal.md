## Why

設定頁面中「常用規則」和「標籤管理」的操作邏輯是：新增/刪除後立即透過 API 保存並顯示通知。但「允許目錄」和「檔案來源白名單」卻採用不同模式——修改只更新本地 state，需要使用者手動點擊「儲存設定」按鈕才會生效。這種不一致的操作體驗容易讓使用者困惑，且可能導致未保存的變更意外遺失。

## What Changes

- 「允許目錄」新增路徑後立即呼叫 API 保存，並顯示成功/失敗通知
- 「允許目錄」刪除路徑後立即呼叫 API 保存，並顯示成功/失敗通知
- 「檔案來源白名單」新增路徑後立即呼叫 API 保存，並顯示成功/失敗通知
- 「檔案來源白名單」刪除路徑後立即呼叫 API 保存，並顯示成功/失敗通知
- 移除底部的「儲存設定」按鈕（所有設定項都改為即時保存後不再需要）

## Capabilities

### New Capabilities

### Modified Capabilities
- `source-path-whitelist`: UI 的新增/刪除操作改為即時保存並顯示通知

## Impact

- **前端**：`SettingView.vue`（`addDirectory`、`removeDirectory`、`addSourceDirectory`、`removeSourceDirectory` 改為 async 並呼叫 API）
- **後端**：無變更（既有的 `PUT /api/v1/settings` 已支援）
