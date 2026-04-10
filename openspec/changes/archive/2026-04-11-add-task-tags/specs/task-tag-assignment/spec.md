## ADDED Requirements

### Requirement: Task 與 Tag 多對多關聯
系統 SHALL 透過 `task_tags` 關聯表維護任務與標籤的多對多關係。

#### Scenario: task_tags 關聯表結構
- **WHEN** 檢查 `task_tags` 資料表
- **THEN** SHALL 包含 `task_id`（FK → task.id）與 `tag_id`（FK → tag.id）欄位，組合為複合主鍵

#### Scenario: 刪除任務時清除關聯
- **WHEN** 刪除一個擁有標籤的任務
- **THEN** 對應的 `task_tags` 記錄 SHALL 自動清除

### Requirement: Task API 回應包含標籤
Task API 的回應 SHALL 包含完整的 tags 資訊。

#### Scenario: 取得任務列表包含標籤
- **WHEN** 發送 `GET /api/v1/tasks`
- **THEN** 每個任務物件 SHALL 包含 `tags` 欄位，為 `Tag[]` 陣列（每個 Tag 含 id, name, color）

#### Scenario: 取得單一任務包含標籤
- **WHEN** 發送 `GET /api/v1/tasks/{task_id}`
- **THEN** 任務物件 SHALL 包含 `tags` 欄位

### Requirement: 建立與更新任務時可指定標籤
TaskCreate 與 TaskUpdate 的請求 body SHALL 支援 `tag_ids` 欄位。

#### Scenario: 建立任務並指定標籤
- **WHEN** 發送 `POST /api/v1/tasks`，body 包含 `tag_ids: ["uuid-1", "uuid-2"]`
- **THEN** SHALL 建立任務並關聯指定標籤

#### Scenario: 更新任務的標籤
- **WHEN** 發送 `PUT /api/v1/tasks/{task_id}`，body 包含 `tag_ids: ["uuid-3"]`
- **THEN** SHALL 更新任務的標籤關聯（替換為新的標籤集合）

#### Scenario: 不傳 tag_ids 時預設空陣列
- **WHEN** 發送 `POST /api/v1/tasks`，body 不包含 `tag_ids` 欄位
- **THEN** 任務 SHALL 建立成功，`tags` 為空陣列

### Requirement: 任務表單標籤選擇器
新增任務與編輯任務的表單 SHALL 包含標籤選擇器，以下拉選單形式從既有標籤中選擇。

#### Scenario: 新增任務時選擇標籤
- **WHEN** 在新增任務表單中開啟標籤選擇器
- **THEN** SHALL 顯示所有可用標籤的下拉選單，每個標籤以彩色 Badge 呈現
- **THEN** 使用者可選擇多個標籤

#### Scenario: 編輯任務時顯示已選標籤
- **WHEN** 開啟任務詳細頁的編輯表單
- **THEN** SHALL 顯示該任務已關聯的標籤
- **THEN** 使用者可新增或移除標籤

### Requirement: Sidebar 任務項目顯示標籤
Sidebar 任務列表中的每個任務項目 SHALL 顯示其關聯的標籤 Badge。

#### Scenario: 任務有標籤時顯示
- **WHEN** 任務擁有一個或多個標籤
- **THEN** 任務項目 SHALL 在名稱下方顯示彩色標籤 Badge

#### Scenario: 任務無標籤時不顯示
- **WHEN** 任務沒有任何標籤
- **THEN** 任務項目 SHALL 不顯示標籤區域
