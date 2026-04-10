## Why

目前 Movera 的任務沒有分類機制，當任務數量增多後難以快速辨識和管理。
新增標籤（Tags）功能讓使用者可以為任務加上彩色標籤（如「動畫」、「電影」、「音樂」），
在 Setting 頁面統一管理全域標籤，並在新增任務與任務詳細頁為任務添加標籤。

## What Changes

- 新增 `Tag` 資料模型（獨立 DB table）與 `task_tags` 多對多關聯表
- 新增 Alembic migration 建立 tag 與 task_tags 表
- 新增 Tag CRUD API（`/api/v1/tags`）
- 修改 Task API 回應包含 tags 資料
- 修改 TaskCreate / TaskUpdate schema 支援 `tag_ids` 欄位
- Setting 頁面新增「標籤管理」區塊（新增、編輯名稱/顏色、刪除）
- TaskForm / TaskEditForm 新增標籤選擇器（下拉選單 + 彩色 Badge 顯示）
- Sidebar 任務列表顯示任務的標籤 Badge

## Capabilities

### New Capabilities

- `tag-management`: 標籤的 CRUD 管理功能，包含 Backend API、Frontend Setting 頁面管理介面
- `task-tag-assignment`: 任務與標籤的關聯功能，包含新增/編輯任務時選擇標籤、UI 顯示

### Modified Capabilities

（無修改既有 spec）

## Impact

- Backend：新增 `backend/models/tag.py`、`backend/routers/tag.py`、`backend/services/tag_service.py`、`backend/repositories/tag_repository.py`
- Backend：修改 `backend/models/task.py`（加入 tags relationship）、`backend/schemas.py`（加入 Tag schemas + 修改 Task schemas）
- Frontend：新增 `src/stores/tagStore.ts`、`src/components/TagBadge.vue`、`src/components/TagSelector.vue`
- Frontend：修改 `src/schemas/index.ts`、`src/views/SettingView.vue`、`src/components/TaskForm.vue`、`src/components/TaskEditForm.vue`、`src/components/SidebarTaskItem.vue`（或對應的 sidebar 任務項目元件）
- Database：新增 `tag` table 與 `task_tags` 關聯表（Alembic migration）
- API：新增 `/api/v1/tags` 端點，修改 `/api/v1/tasks` 回應格式
