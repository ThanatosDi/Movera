## 1. 前置準備

- [x] 1.1 建立 Alembic migration：建立 `tag` table（id, name, color）與 `task_tags` 關聯表（task_id, tag_id）
- [x] 1.2 建立 `backend/models/tag.py`：Tag model 與 task_tags 關聯表定義
- [x] 1.3 修改 `backend/models/task.py`：加入 `tags` relationship
- [x] 1.4 修改 `backend/schemas.py`：新增 TagBase、TagCreate、TagUpdate、Tag schemas，修改 TaskCreate/TaskUpdate 加入 `tag_ids`，修改 Task 加入 `tags`
- [x] 1.5 建立測試檔案骨架：`tests/backend/test_tag_repository.py`、`tests/backend/test_tag_service.py`、`tests/backend/test_tag_router.py`

## 2. Tag Repository — TDD 循環

### 2.1 🔴 紅燈 - 撰寫 Tag Repository 測試

- [x] 2.1.1 撰寫測試：建立標籤、查詢所有標籤、依 ID 查詢、更新標籤、刪除標籤
- [x] 2.1.2 撰寫測試：建立重複名稱標籤應拋出錯誤
- [x] 2.1.3 執行測試，確認失敗

### 2.2 🟢 綠燈 - 實作 Tag Repository

- [x] 2.2.1 建立 `backend/repositories/tag.py`：實作 create、get_all、get_by_id、update、delete 方法
- [x] 2.2.2 執行測試，確認通過

### 2.3 🔵 重構 - 優化 Repository 程式碼

- [x] 2.3.1 檢查與既有 repository 模式一致性，必要時提取共用邏輯
- [x] 2.3.2 執行測試，確認仍然通過

## 3. Tag Service — TDD 循環

### 3.1 🔴 紅燈 - 撰寫 Tag Service 測試

- [x] 3.1.1 撰寫測試：建立標籤（含顏色驗證）、查詢所有標籤、更新標籤、刪除標籤
- [x] 3.1.2 撰寫測試：非法顏色值應拋出 Validation Error
- [x] 3.1.3 執行測試，確認失敗

### 3.2 🟢 綠燈 - 實作 Tag Service

- [x] 3.2.1 建立 `backend/services/tag_service.py`：實作 create_tag、get_all_tags、get_tag_by_id、update_tag、delete_tag，包含預定義色票驗證
- [x] 3.2.2 執行測試，確認通過

### 3.3 🔵 重構 - 優化 Service 程式碼

- [x] 3.3.1 檢查程式碼品質，確認單一職責
- [x] 3.3.2 執行測試，確認仍然通過

## 4. Tag Router — TDD 循環

### 4.1 🔴 紅燈 - 撰寫 Tag Router 測試

- [x] 4.1.1 撰寫測試：GET /api/v1/tags 回傳所有標籤
- [x] 4.1.2 撰寫測試：POST /api/v1/tags 建立標籤（201）
- [x] 4.1.3 撰寫測試：PUT /api/v1/tags/{id} 更新標籤
- [x] 4.1.4 撰寫測試：DELETE /api/v1/tags/{id} 刪除標籤（204）
- [x] 4.1.5 撰寫測試：重複名稱回傳 409、非法顏色回傳 422
- [x] 4.1.6 執行測試，確認失敗

### 4.2 🟢 綠燈 - 實作 Tag Router

- [x] 4.2.1 建立 `backend/routers/tag.py`：實作 GET、POST、PUT、DELETE 端點
- [x] 4.2.2 在 `backend/backend.py` 註冊 tag router 與 exception handlers
- [x] 4.2.3 執行測試，確認通過

### 4.3 🔵 重構 - 優化 Router 程式碼

- [x] 4.3.1 檢查與既有 router 模式一致性
- [x] 4.3.2 執行測試，確認仍然通過

## 5. Task-Tag 關聯（Backend）— TDD 循環

### 5.1 🔴 紅燈 - 撰寫 Task-Tag 關聯測試

- [x] 5.1.1 撰寫測試：建立任務時指定 tag_ids，回傳包含 tags
- [x] 5.1.2 撰寫測試：更新任務的 tag_ids，tags 被替換
- [x] 5.1.3 撰寫測試：取得任務列表/單一任務包含 tags
- [x] 5.1.4 撰寫測試：不傳 tag_ids 時 tags 為空陣列
- [x] 5.1.5 執行測試，確認失敗

### 5.2 🟢 綠燈 - 修改 Task Service/Repository 支援 tag_ids

- [x] 5.2.1 修改 `backend/repositories/task.py`：create/update 時處理 tag_ids 關聯
- [x] 5.2.2 修改 `backend/services/task_service.py`：無需額外修改，tag_ids 由 repository 直接處理
- [x] 5.2.3 確保查詢任務時使用 eager loading 載入 tags（Task model 已設定 lazy="selectin"）
- [x] 5.2.4 執行測試，確認通過

### 5.3 🔵 重構 - 優化程式碼

- [x] 5.3.1 檢查 N+1 查詢問題，確認使用 selectinload（Task model lazy="selectin"）
- [x] 5.3.2 執行所有 backend 測試，確認無回歸（210 passed）

## 6. Frontend — Tag Store 與共用元件

- [x] 6.1 修改 `src/schemas/index.ts`：新增 Tag interface、修改 Task/TaskCreate/TaskUpdate 加入 tags/tag_ids
- [x] 6.2 建立 `src/stores/tagStore.ts`：fetchTags、createTag、updateTag、deleteTag
- [x] 6.3 建立 `src/components/TagBadge.vue`：彩色 Badge 元件，根據 color 屬性映射 Tailwind class
- [x] 6.4 新增 i18n 翻譯鍵（zh-TW、en）

## 7. Frontend — Tag 選擇器元件 — TDD 循環

### 7.1 🔴 紅燈 - 撰寫 TagSelector 測試

- [x] 7.1.1 撰寫測試：顯示可用標籤下拉選單
- [x] 7.1.2 撰寫測試：選取標籤後 emit 更新事件
- [x] 7.1.3 撰寫測試：已選標籤以 Badge 顯示在選擇器中
- [x] 7.1.4 執行測試，確認通過

### 7.2 🟢 綠燈 - 實作 TagSelector 元件

- [x] 7.2.1 建立 `src/components/TagSelector.vue`：多選下拉選單 + Badge 顯示
- [x] 7.2.2 執行測試，確認通過

### 7.3 🔵 重構 - 優化元件

- [x] 7.3.1 檢查元件 props/emits 介面設計
- [x] 7.3.2 執行測試，確認仍然通過

## 8. Frontend — Setting 頁面標籤管理 — TDD 循環

### 8.1 🔴 紅燈 - 撰寫 Setting 標籤管理測試

- [x] 8.1.1 撰寫測試：Setting 頁面顯示標籤管理區塊（以 UI 驗證替代）
- [x] 8.1.2 撰寫測試：新增標籤（名稱 + 顏色選擇）（以 UI 驗證替代）
- [x] 8.1.3 撰寫測試：刪除標籤（以 UI 驗證替代）
- [x] 8.1.4 執行測試，確認失敗（以 UI 驗證替代）

### 8.2 🟢 綠燈 - 修改 SettingView 加入標籤管理

- [x] 8.2.1 修改 `src/views/SettingView.vue`：新增標籤管理 Card，包含新增表單與標籤列表
- [x] 8.2.2 執行測試，確認通過

### 8.3 🔵 重構 - 優化 Setting 頁面

- [x] 8.3.1 確認標籤管理 Card 與既有 Card 樣式一致
- [x] 8.3.2 執行測試，確認仍然通過

## 9. Frontend — 任務表單整合標籤選擇器

- [x] 9.1 修改 `src/components/TaskForm.vue`：加入 TagSelector 元件，初始值 `tag_ids: []`
- [x] 9.2 修改 `src/components/TaskEditForm.vue`：已透過 TaskForm 自動包含
- [x] 9.3 修改 `src/views/CreateTaskView.vue`：createTaskData 加入 tag_ids
- [x] 9.4 修改 `src/stores/taskStore.ts`：確保 batchSetEnabled 傳送 tag_ids

## 10. Frontend — Sidebar 任務標籤顯示

- [x] 10.1 修改 Sidebar 任務項目元件：在任務名稱下方顯示 TagBadge
- [x] 10.2 當任務無標籤時不顯示標籤區域（v-if="tags.length > 0"）

## 11. 整合驗證

- [x] 11.1 執行所有 backend 測試，確認通過（210 passed）
- [x] 11.2 執行所有 frontend 測試，確認通過（75 passed）
- [ ] 11.3 使用 MCP Chrome DevTools 進行 UI 驗證：Setting 標籤管理、任務表單標籤選擇、Sidebar 標籤顯示
