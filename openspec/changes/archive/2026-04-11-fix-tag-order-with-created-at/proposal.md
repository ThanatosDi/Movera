## Why

標籤在各個頁面的顯示順序不一致且不可預測，因為目前的 `tag` 表和 `task_tags` 關聯表都沒有時間戳記欄位。
需要加入 `created_at` 欄位，讓所有標籤顯示都能按建立時間排序，確保：
1. Sidebar 任務標籤依加入順序顯示
2. 任務詳細頁中的標籤依加入順序顯示
3. Setting 頁面的標籤依建立時間排序

## What Changes

- `tag` 表加入 `created_at` 欄位（DateTime, not null, default=now）
- `task_tags` 關聯表加入 `created_at` 欄位（DateTime, not null, default=now），代表標籤被加入任務的時刻
- 新增 Alembic migration
- 修改 Tag model 與 task_tags 定義
- Task model 的 tags relationship 加入 `order_by` 按 `task_tags.c.created_at` 排序
- Tag API 回傳按 `created_at` 排序
- 前端 Tag schema 加入 `created_at` 欄位

## Capabilities

### New Capabilities

（無新增 capability）

### Modified Capabilities

（無修改既有 spec）

## Impact

- Backend：`backend/models/tag.py`（加入 created_at 欄位）
- Backend：`backend/repositories/tag.py`、`backend/repositories/task.py`（排序邏輯）
- Backend：`backend/schemas.py`（Tag schema 加入 created_at）
- Database：新增 Alembic migration
- Frontend：`src/schemas/index.ts`（Tag interface 加入 created_at）
