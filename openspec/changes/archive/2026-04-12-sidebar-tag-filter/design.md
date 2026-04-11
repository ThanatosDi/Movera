## Context

目前 Sidebar 顯示所有任務清單，任務資料已包含 `tags` 陣列。系統已有完整的 Tag CRUD 功能（`tagStore`）與 Tag 顯示元件（`TagBadge`），但缺乏基於 Tag 的篩選機制。所有篩選將在前端完成，不需要後端 API 變更。

現有相關元件：
- `src/layouts/Sidebar.vue` — 主 Sidebar，渲染任務清單
- `src/stores/taskStore.ts` — 任務狀態管理，已有 `tasks` state
- `src/stores/tagStore.ts` — 標籤狀態管理，提供所有標籤清單
- `src/components/TagBadge.vue` — 標籤顯示元件（含顏色樣式）

## Goals / Non-Goals

**Goals:**
- 讓使用者在 Sidebar 中透過點擊 Tag 來篩選任務
- 支援多 Tag 篩選
- 篩選狀態純前端管理，無需後端變更
- 與現有的選擇模式（selection mode）和批次操作相容

**Non-Goals:**
- 不實作後端篩選 API（任務數量有限，前端篩選即可）
- 不實作搜尋文字篩選（僅 Tag 篩選）
- 不修改 Tag 管理功能本身
- 不持久化篩選狀態（重新整理頁面後重置）

## Decisions

### 1. 篩選狀態放在 taskStore（Store 層）

將 `selectedFilterTagIds: Set<string>` 新增至 `taskStore`，並提供 `filteredTasks` computed property。

**理由**: 篩選後的任務清單可能需要在多個地方使用（Sidebar、批次操作計數等），放在 Store 中方便共享。比放在 Sidebar 元件的 local state 更具擴展性。

**替代方案**: 使用 Sidebar 的 local ref — 較簡單但限制了未來其他元件存取篩選結果的能力。

### 2. 多 Tag 篩選採用聯集（Union）邏輯

選擇多個 Tag 時，顯示包含「任一」選中 Tag 的任務（OR 邏輯）。

**理由**: 聯集邏輯更直覺 — 使用者期望選擇更多 Tag 會看到更多結果，而非更少。且對於標籤分類的使用情境（如：動畫、電影），使用者通常想看「動畫或電影」的任務。

**替代方案**: 交集（AND）邏輯 — 選越多 Tag 結果越少，容易造成空結果的困惑。

### 3. 篩選 UI 使用可收合的 Tag 列表元件

在 Sidebar 的建立任務按鈕與 SidebarTool 之間新增 `SidebarTagFilter` 元件，以水平排列的 `TagBadge` 呈現，點擊切換選取狀態。提供收合/展開功能以節省空間。

**理由**: 使用現有的 `TagBadge` 元件保持視覺一致性。可收合設計避免在標籤數量較多時佔據過多 Sidebar 空間。

**替代方案**: 使用下拉選單 — 需額外點擊才能看到標籤，不如直接可見直覺。

### 4. 影響層級

| 層級 | 影響 |
|------|------|
| Component | 新增 `SidebarTagFilter.vue`；修改 `Sidebar.vue` 引入篩選元件 |
| Store | 修改 `taskStore.ts` 新增篩選 state 與 computed |
| i18n | 新增篩選相關翻譯 key |

## Risks / Trade-offs

- **[標籤數量過多導致 UI 擁擠]** → 透過可收合設計緩解；預設收合狀態可在標籤多時保持 Sidebar 整潔
- **[篩選與選擇模式的互動]** → 篩選後進入選擇模式僅操作篩選後的任務，批次操作的 `selectAllTasks` 應參考 `filteredTasks` 而非 `tasks`
- **[篩選狀態不持久化]** → 頁面重新整理或切換路由後篩選重置，這是刻意的設計選擇以保持簡單性
