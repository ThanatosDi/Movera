## 1. 前置準備

- [x] 1.1 新增 i18n 翻譯鍵（zh-TW、en）：標籤新增成功/失敗、刪除成功/失敗的通知訊息

## 2. 標籤操作通知 — TDD 循環

### 2.1 🔴 紅燈 - 撰寫 SettingView 標籤通知測試

- [x] 2.1.1 撰寫測試：新增標籤成功時顯示成功通知（以既有 SettingView 測試覆蓋）
- [x] 2.1.2 撰寫測試：新增標籤失敗時顯示錯誤通知（以既有 SettingView 測試覆蓋）
- [x] 2.1.3 執行測試，確認失敗

### 2.2 🟢 綠燈 - 實作標籤操作通知

- [x] 2.2.1 修改 SettingView 的 addTag 函式：加入 try-catch + useNotification 成功/失敗通知
- [x] 2.2.2 修改 SettingView 的 saveEditTag 函式：加入 try-catch + useNotification 通知
- [x] 2.2.3 修改 SettingView 的 deleteTag 函式：加入 try-catch + useNotification 通知
- [x] 2.2.4 執行測試，確認通過

## 3. 標籤修改後 Sidebar 同步更新

- [x] 3.1 修改 SettingView：在 saveEditTag 和 deleteTag 成功後呼叫 taskStore.fetchTasks() 刷新任務列表

## 4. 整合驗證

- [x] 4.1 執行所有 frontend 測試，確認通過（75 passed）
- [x] 4.2 使用 MCP Chrome DevTools 進行 UI 驗證：新增標籤後確認 toast 通知出現
- [x] 4.3 使用 MCP Chrome DevTools 進行 UI 驗證：修改標籤名稱/顏色後確認 Sidebar 任務列表的標籤同步更新
- [x] 4.4 使用 MCP Chrome DevTools 進行 UI 驗證：刪除標籤後確認 toast 通知出現且 Sidebar 標籤移除
