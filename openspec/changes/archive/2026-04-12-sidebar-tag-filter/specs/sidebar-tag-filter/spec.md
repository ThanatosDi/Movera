## ADDED Requirements

### Requirement: Sidebar 顯示 Tag 篩選區域
系統 SHALL 在 Sidebar 的建立任務按鈕下方顯示一個 Tag 篩選區域，呈現所有可用的 Tag。每個 Tag SHALL 使用與 `TagBadge` 一致的顏色樣式顯示。當系統中無任何 Tag 時，篩選區域 SHALL 隱藏不顯示。

#### Scenario: 有 Tag 時顯示篩選區域
- **WHEN** 系統中存在至少一個 Tag
- **THEN** Sidebar 在建立任務按鈕下方顯示 Tag 篩選區域，列出所有 Tag

#### Scenario: 無 Tag 時隱藏篩選區域
- **WHEN** 系統中不存在任何 Tag
- **THEN** Sidebar 不顯示 Tag 篩選區域

### Requirement: 點擊 Tag 切換篩選狀態
使用者 SHALL 能透過點擊 Tag 來切換其選取狀態。選取的 Tag SHALL 呈現明顯的視覺區分（如高亮或外框），未選取的 Tag SHALL 呈現淡化樣式。

#### Scenario: 選取一個 Tag
- **WHEN** 使用者點擊一個未選取的 Tag
- **THEN** 該 Tag 切換為選取狀態，呈現高亮樣式

#### Scenario: 取消選取一個 Tag
- **WHEN** 使用者點擊一個已選取的 Tag
- **THEN** 該 Tag 切換為未選取狀態，恢復淡化樣式

### Requirement: Tag 篩選以聯集邏輯過濾任務
當一個或多個 Tag 被選取時，Sidebar 的任務清單 SHALL 僅顯示包含「任一」選取 Tag 的任務（OR 邏輯）。未選取任何 Tag 時 SHALL 顯示全部任務。

#### Scenario: 未選取任何 Tag
- **WHEN** 沒有任何 Tag 被選取
- **THEN** Sidebar 顯示所有任務

#### Scenario: 選取單一 Tag 篩選
- **WHEN** 使用者選取一個 Tag「動畫」
- **THEN** Sidebar 僅顯示包含「動畫」Tag 的任務

#### Scenario: 選取多個 Tag 篩選（聯集）
- **WHEN** 使用者選取「動畫」和「電影」兩個 Tag
- **THEN** Sidebar 顯示包含「動畫」或「電影」（或兩者皆有）的任務

#### Scenario: 篩選結果為空
- **WHEN** 使用者選取的 Tag 沒有對應任何任務
- **THEN** Sidebar 顯示空狀態提示

### Requirement: 篩選區域可收合
Tag 篩選區域 SHALL 支援收合與展開。使用者 SHALL 能透過點擊標題區域來切換收合狀態。

#### Scenario: 展開篩選區域
- **WHEN** 使用者點擊已收合的篩選區域標題
- **THEN** 篩選區域展開，顯示所有 Tag

#### Scenario: 收合篩選區域
- **WHEN** 使用者點擊已展開的篩選區域標題
- **THEN** 篩選區域收合，隱藏 Tag 列表

#### Scenario: 收合時顯示已選取 Tag 數量
- **WHEN** 篩選區域處於收合狀態且有 Tag 被選取
- **THEN** 標題旁顯示已選取的 Tag 數量

### Requirement: 篩選與批次操作相容
當 Tag 篩選啟用時，選擇模式的「全選」功能 SHALL 僅選取篩選後的任務。批次操作（啟用、停用、刪除）SHALL 僅作用於已選取的任務。

#### Scenario: 篩選後全選
- **WHEN** Tag 篩選啟用且使用者點擊「全選」
- **THEN** 僅篩選結果中的任務被選取，非篩選結果的任務不被選取

#### Scenario: 篩選後批次操作
- **WHEN** Tag 篩選啟用且使用者執行批次停用
- **THEN** 僅被選取的（篩選結果中的）任務被停用
