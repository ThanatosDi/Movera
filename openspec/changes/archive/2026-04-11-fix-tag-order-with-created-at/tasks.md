## 1. 前置準備

- [x] 1.1 修改 `backend/models/tag.py`：Tag model 加入 `created_at` 欄位（DateTime, not null, default=now）
- [x] 1.2 修改 `backend/models/tag.py`：task_tags Table 加入 `created_at` Column（DateTime, not null, server_default=func.now()）
- [x] 1.3 修改 `backend/models/task.py`：tags relationship 加入 `order_by=task_tags.c.created_at.asc()`
- [x] 1.4 修改 `backend/schemas.py`：Tag_ schema 加入 `created_at: datetime` 欄位
- [x] 1.5 建立 Alembic migration：為 tag 表加入 created_at、為 task_tags 表加入 created_at

## 2. Tag 排序 — TDD 循環

### 2.1 🔴 紅燈 - 撰寫排序測試

- [x] 2.1.1 撰寫測試：TagRepository get_all 回傳按 created_at ASC 排序
- [x] 2.1.2 撰寫測試：Task 的 tags 按 task_tags.created_at ASC 排序
- [x] 2.1.3 執行測試，確認失敗（task_tags order 1 failed）

### 2.2 🟢 綠燈 - 實作排序邏輯

- [x] 2.2.1 修改 `backend/repositories/tag.py`：get_all 加入 order_by(Tag.created_at.asc())
- [x] 2.2.2 執行測試，確認通過（2 passed）

## 3. Frontend Schema 更新

- [x] 3.1 修改 `src/schemas/index.ts`：Tag interface 加入 `created_at: string`

## 4. 整合驗證

- [x] 4.1 執行所有 backend 測試，確認無回歸（212 passed）
- [x] 4.2 執行所有 frontend 測試，確認通過（75 passed）
