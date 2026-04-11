## Why

目前 Sidebar 顯示所有任務，當任務數量增加時難以快速找到特定類型的任務。雖然系統已有完整的 Tag 管理功能（建立、指派、顯示），但尚未提供基於 Tag 的篩選機制。新增 Tag 篩選功能可讓使用者透過標籤快速過濾任務清單，大幅提升操作效率。

## What Changes

- 在 Sidebar 頂部（建立任務按鈕下方）新增 Tag 篩選區域，顯示所有可用的 Tag
- 使用者可點擊一個或多個 Tag 來篩選 Sidebar 中的任務清單
- 選中 Tag 後，僅顯示包含該 Tag 的任務；未選擇任何 Tag 時顯示全部任務
- 支援多 Tag 篩選（交集或聯集邏輯）
- 篩選狀態在前端管理，無需後端 API 變更

## Capabilities

### New Capabilities
- `sidebar-tag-filter`: Sidebar 中的 Tag 篩選 UI 元件與篩選邏輯，允許使用者透過點擊 Tag 來過濾任務清單

### Modified Capabilities

（無需修改現有 capability 的需求規格）

## Impact

- **前端元件**: 新增篩選元件於 `src/layouts/Sidebar.vue`，可能抽取為獨立元件
- **狀態管理**: `taskStore` 需新增篩選相關的 state 與 computed properties
- **現有元件**: `SidebarItem` 與 `SidebarTool` 不需修改，僅由篩選後的任務清單驅動顯示
- **後端**: 無需變更，所有篩選在前端完成（任務已包含 tags 資料）
- **依賴**: 使用現有的 `tagStore` 取得標籤清單，使用現有的 `TagBadge` 元件風格
