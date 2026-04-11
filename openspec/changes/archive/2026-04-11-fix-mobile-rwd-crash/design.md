## Context

新增標籤功能後，`SidebarItem` 的 `tags` prop 從選填變成必填（使用 `defineProps<{}>`），但 `TasksListView.vue` 未同步更新傳入 `:tags`。同時 `Layout.vue` 的 `<main>` 缺少底部 padding，內容底部可能被手機底部導覽列遮擋。

影響層級：View（TasksListView）、Layout（Layout.vue）

## Goals / Non-Goals

**Goals:**
- 修正任務頁面在手機版白屏的 crash
- 確保所有手機版頁面底部不被導覽列遮擋

**Non-Goals:**
- 不重構 Sidebar / Layout 架構

## Decisions

### 1. 為 TasksListView 的 SidebarItem 傳入 tags prop

直接加入 `:tags="task.tags || []"`，與 `Sidebar.vue` 的寫法一致。

### 2. 為 Layout.vue 的 main 加入手機版底部 padding

加入 `pb-20 sm:pb-4` class，在手機版預留底部導覽列空間。

## Risks / Trade-offs

- 風險極低，僅修正 props 傳遞和 CSS class
