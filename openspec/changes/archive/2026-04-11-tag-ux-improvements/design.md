## Context

Setting 頁面的標籤 CRUD 操作目前沒有 toast 通知，且修改標籤後 Sidebar 不會同步更新。
專案已有 `useNotification` composable（`showSuccess`、`showError`）和 i18n 通知模式可參考。

影響層級：View（SettingView.vue）

## Goals / Non-Goals

**Goals:**
- 標籤新增/刪除成功時顯示 success toast
- 標籤新增/刪除失敗時顯示 error toast
- 修改標籤（名稱/顏色）後，Sidebar 任務列表中的標籤同步更新

**Non-Goals:**
- 不修改標籤編輯的 inline editing UI 本身
- 不新增確認 dialog（刪除前確認等）

## Decisions

### 1. 在 SettingView 的 addTag/saveEditTag/deleteTag 加入 try-catch + toast

沿用既有的 `useNotification.showSuccess` / `showError` 模式，與 Setting 頁面儲存設定的通知風格一致。

### 2. 修改/刪除標籤後呼叫 taskStore.fetchTasks() 刷新任務列表

理由：最簡單且可靠的方式確保 Sidebar 的 `task.tags` 與 DB 同步。避免在前端手動遍歷 tasks 做 tag 物件替換，降低複雜度。

替代方案：前端遍歷 `taskStore.tasks` 並替換對應 tag 物件 — 但增加前端複雜度，且可能有遺漏。

## Risks / Trade-offs

- [取捨] 修改標籤後會多一次 GET /api/v1/tasks 請求 → 對 12 個任務的小型列表影響可忽略
