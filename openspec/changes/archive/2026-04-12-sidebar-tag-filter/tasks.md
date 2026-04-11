## 1. 前置準備

- [x] 1.1 新增 i18n 翻譯 key（`sidebar.tagFilter.title`、`sidebar.tagFilter.selected`、`sidebar.tagFilter.noResults` 等）
- [x] 1.2 建立 `SidebarTagFilter.vue` 元件骨架與測試檔案

## 2. taskStore 篩選狀態（TDD 循環）

### 2.1 🔴 紅燈 - 撰寫 taskStore 篩選邏輯測試

- [x] 2.1.1 測試：`selectedFilterTagIds` 初始為空集合
- [x] 2.1.2 測試：`toggleFilterTag(tagId)` 切換 Tag 選取狀態
- [x] 2.1.3 測試：`clearFilterTags()` 清除所有篩選
- [x] 2.1.4 測試：`filteredTasks` 在未選取 Tag 時返回全部任務
- [x] 2.1.5 測試：`filteredTasks` 在選取單一 Tag 時僅返回包含該 Tag 的任務
- [x] 2.1.6 測試：`filteredTasks` 在選取多個 Tag 時使用聯集邏輯
- [x] 2.1.7 測試：`filteredTasks` 篩選結果為空時返回空陣列
- [x] 2.1.8 執行測試，確認全部失敗

### 2.2 🟢 綠燈 - 實作 taskStore 篩選功能

- [x] 2.2.1 在 `taskStore` 新增 `selectedFilterTagIds` state（`Set<string>`）
- [x] 2.2.2 新增 `toggleFilterTag(tagId: string)` action
- [x] 2.2.3 新增 `clearFilterTags()` action
- [x] 2.2.4 新增 `filteredTasks` computed property（聯集邏輯）
- [x] 2.2.5 執行測試，確認全部通過

### 2.3 🔵 重構 - 優化 taskStore 篩選程式碼

- [x] 2.3.1 確認 `filteredTasks` 效能（避免不必要的重新計算）
- [x] 2.3.2 確認 `selectAllTasks` 參考 `filteredTasks` 而非 `tasks`
- [x] 2.3.3 執行測試，確認仍然通過

## 3. SidebarTagFilter 元件（TDD 循環）

### 3.1 🔴 紅燈 - 撰寫 SidebarTagFilter 元件測試

- [x] 3.1.1 測試：無 Tag 時不渲染元件
- [x] 3.1.2 測試：有 Tag 時渲染所有 Tag 為可點擊的 TagBadge
- [x] 3.1.3 測試：點擊 Tag 呼叫 `toggleFilterTag`
- [x] 3.1.4 測試：已選取的 Tag 呈現高亮樣式
- [x] 3.1.5 測試：點擊標題切換收合/展開狀態
- [x] 3.1.6 測試：收合時顯示已選取 Tag 數量
- [x] 3.1.7 執行測試，確認全部失敗

### 3.2 🟢 綠燈 - 實作 SidebarTagFilter 元件

- [x] 3.2.1 建立 `SidebarTagFilter.vue`，使用 `tagStore` 取得所有 Tag
- [x] 3.2.2 渲染 Tag 列表，使用 `TagBadge` 元件樣式
- [x] 3.2.3 實作點擊 Tag 切換篩選（已選取/未選取的視覺區分）
- [x] 3.2.4 實作收合/展開功能與收合時的選取數量顯示
- [x] 3.2.5 執行測試，確認全部通過

### 3.3 🔵 重構 - 優化 SidebarTagFilter 元件

- [x] 3.3.1 確認樣式與現有 Sidebar 元件一致
- [x] 3.3.2 確認 i18n 翻譯正確套用
- [x] 3.3.3 執行測試，確認仍然通過

## 4. Sidebar 整合

- [x] 4.1 在 `Sidebar.vue` 中引入 `SidebarTagFilter` 元件（置於建立任務按鈕與 SidebarTool 之間）
- [x] 4.2 將 Sidebar 任務清單的資料來源從 `tasks` 改為 `filteredTasks`
- [x] 4.3 確認篩選與選擇模式（selection mode）正常搭配運作

## 5. 整合測試與品質檢查

- [ ] 5.1 使用 MCP Chrome DevTools 進行 E2E 測試：驗證 Tag 篩選 UI 互動流程
- [x] 5.2 確認無 Tag 時篩選區域隱藏
- [x] 5.3 確認篩選後批次操作僅影響篩選結果中的任務
- [x] 5.4 執行完整前端測試套件，確認無回歸
