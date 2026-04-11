## Context

目前 `tag` 表沒有 `created_at`，`task_tags` 關聯表也沒有時間欄位。
標籤在各頁面的顯示順序依賴 DB 返回的不確定順序。

影響層級：Model → Repository → Schema → Migration → Frontend Schema

## Goals / Non-Goals

**Goals:**
- `tag` 表加入 `created_at`，Setting 頁面按建立時間排序標籤
- `task_tags` 關聯表加入 `created_at`，表示標籤被加入任務的時刻
- Task 的 tags relationship 按 `task_tags.created_at` ASC 排序
- Tag API（GET /api/v1/tags）按 `tag.created_at` ASC 排序

**Non-Goals:**
- 不做標籤手動排序功能
- 不修改前端排序邏輯（由 API 回傳順序決定）

## Decisions

### 1. task_tags 從 Table 改為 ORM Model

需要在 `task_tags` 加入 `created_at` 欄位，SQLAlchemy Table 定義不方便加入 default 值和 relationship order_by。
但實際上 SQLAlchemy Table 可以加 Column 帶 `server_default`，不需要改成 ORM Model。
保持 Table 定義，加入 `created_at` Column with `server_default=func.now()`。

### 2. Tag relationship order_by

Task model 的 `tags` relationship 加入 `order_by=task_tags.c.created_at.asc()`。

### 3. TagRepository get_all 排序

`get_all()` 改為 `query(Tag).order_by(Tag.created_at.asc()).all()`。

## Risks / Trade-offs

- [風險] 既有的 task_tags 記錄沒有 created_at → migration 中使用 `server_default` 填充
- [風險] 既有的 tag 記錄沒有 created_at → migration 中使用 `server_default` 填充
