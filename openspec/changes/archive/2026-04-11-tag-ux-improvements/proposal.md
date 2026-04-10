## Why

標籤管理的 UI/UX 有兩個待改善項目：
1. 新增/刪除標籤後沒有任何成功或失敗的通知回饋，使用者不確定操作是否成功
2. 在 Setting 頁面修改標籤（名稱或顏色）後，Sidebar 任務列表中套用該標籤的任務仍顯示舊的標籤資訊，需重新整理才會更新

## What Changes

- Setting 頁面的 `addTag`、`saveEditTag`、`deleteTag` 函式加入 toast 通知（成功/失敗）
- 修改標籤後重新取得任務列表，確保 Sidebar 的標籤同步更新
- 新增對應的 i18n 翻譯鍵

## Capabilities

### New Capabilities

（無新增 capability）

### Modified Capabilities

（無修改既有 spec — 此為純 UI/UX 體驗優化，不涉及行為規格變更）

## Impact

- Frontend：`src/views/SettingView.vue`（加入通知與任務列表刷新）
- Frontend：`src/locales/zh-TW.json`、`src/locales/en.json`（新增通知翻譯鍵）
