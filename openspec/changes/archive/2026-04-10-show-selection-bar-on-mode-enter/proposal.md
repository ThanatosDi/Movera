## Why

目前「已選擇 N 項」批量操作列只有在選擇模式啟用**且**已選取至少一個任務時才會顯示。
這導致使用者進入選擇模式後看不到操作列，需要先勾選任務才能發現批量操作功能的存在，體驗不直覺。
應改為只要進入選擇模式就立即顯示操作列（顯示「已選擇 0 項」），讓使用者一眼看到可用操作。

## What Changes

- 修改 `SidebarTool.vue` 的批量操作列顯示條件：從 `isSelectMode && selectedCount > 0` 改為 `isSelectMode`
- 批量操作按鈕在 `selectedCount === 0` 時應禁用（disabled），避免觸發無意義的空操作

## Capabilities

### New Capabilities

（無新增 capability）

### Modified Capabilities

（無修改既有 spec）

## Impact

- 前端元件：`src/components/SidebarTool.vue`（僅 template 層級修改）
- 不影響 API、後端邏輯、或其他元件
