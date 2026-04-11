## Why

手機版（< 640px）下點擊底部導覽列的「任務」頁面會白屏，原因是 `TasksListView.vue` 使用 `SidebarItem` 元件時未傳入必要的 `tags` prop，導致 `SidebarItem` 內的 `tags.length` 存取 `undefined` 而崩潰，整個路由渲染失敗。

## What Changes

- 修正 `TasksListView.vue`：為 `SidebarItem` 加入 `:tags="task.tags || []"` prop
- 修正 `Layout.vue`：為 `<main>` 加入底部 padding，避免內容被固定底部導覽列遮擋

## Capabilities

### New Capabilities

（無新增 capability）

### Modified Capabilities

（無修改既有 spec）

## Impact

- Frontend：`src/views/TasksListView.vue`（修正 SidebarItem props）
- Frontend：`src/layouts/Layout.vue`（修正 main padding）
