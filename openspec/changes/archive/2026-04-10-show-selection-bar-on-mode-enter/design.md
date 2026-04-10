## Context

`SidebarTool.vue` 的批量操作列（「已選擇 N 項」+ 啟用/停用/刪除按鈕）目前以 `v-if="isSelectMode && selectedCount > 0"` 控制顯示。
使用者進入選擇模式後，操作列不可見，需先勾選任務才會出現，體驗不直覺。

影響層級：Component（`SidebarTool.vue`）

## Goals / Non-Goals

**Goals:**
- 進入選擇模式時立即顯示批量操作列（顯示「已選擇 0 項」）
- 未選取任何任務時，批量操作按鈕應為 disabled 狀態，防止空操作

**Non-Goals:**
- 不修改 taskStore 邏輯
- 不調整操作列的視覺樣式或佈局

## Decisions

### 1. 修改 v-if 條件而非調整 store 邏輯

將 `v-if="isSelectMode && selectedCount > 0"` 改為 `v-if="isSelectMode"`。

理由：問題出在 template 的顯示條件，store 的 `isSelectMode` 和 `selectedTaskIds` 狀態管理本身是正確的，不需要改動。

### 2. 使用 `:disabled` 禁用空選取時的按鈕

為三個批量操作按鈕加上 `:disabled="selectedCount === 0"`。

理由：操作列顯示但按鈕不可點擊，比隱藏整個操作列更能引導使用者理解「先選取再操作」的流程。

## Risks / Trade-offs

- [風險] 使用者可能誤以為按鈕壞了 → 透過 disabled 樣式（灰色、cursor-not-allowed）清楚提示
- 變更範圍極小（僅 `SidebarTool.vue` template），無回歸風險
