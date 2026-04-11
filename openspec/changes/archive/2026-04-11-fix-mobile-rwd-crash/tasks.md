## 1. 修正 TasksListView SidebarItem tags prop

- [x] 1.1 修改 `src/views/TasksListView.vue`：為 SidebarItem 加入 `:tags="task.tags || []"` prop

## 2. 修正 Layout 手機版底部 padding

- [x] 2.1 修改 `src/layouts/Layout.vue`：為 main 加入 `pb-20 sm:pb-4` class

## 3. 整合驗證

- [x] 3.1 執行所有 frontend 測試，確認通過（75 passed）
- [x] 3.2 使用 MCP Chrome DevTools 模擬手機尺寸（375x812），驗證任務頁面正常渲染
- [x] 3.3 使用 MCP Chrome DevTools 驗證建立任務頁面正常渲染
- [x] 3.4 使用 MCP Chrome DevTools 驗證設定頁面底部不被導覽列遮擋
