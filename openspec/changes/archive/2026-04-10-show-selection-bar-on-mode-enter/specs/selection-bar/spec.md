## ADDED Requirements

### Requirement: 選擇模式啟用時立即顯示批量操作列
當使用者進入選擇模式時，批量操作列（包含選取計數與操作按鈕）SHALL 立即顯示，無論是否已選取任何任務。

#### Scenario: 進入選擇模式未選取任務
- **WHEN** 使用者點擊「選擇模式」按鈕進入選擇模式
- **THEN** 批量操作列 SHALL 立即顯示，顯示「已選擇 0 項」

#### Scenario: 選取任務後計數更新
- **WHEN** 使用者在選擇模式中勾選一個任務
- **THEN** 操作列 SHALL 顯示「已選擇 1 項」

### Requirement: 未選取任務時批量操作按鈕禁用
當選取數量為 0 時，批量操作按鈕（啟用、停用、刪除）SHALL 為 disabled 狀態，防止觸發空操作。

#### Scenario: 零選取時按鈕禁用
- **WHEN** 選擇模式已啟用且未選取任何任務
- **THEN** 啟用、停用、刪除三個批量操作按鈕 SHALL 為 disabled 狀態

#### Scenario: 有選取時按鈕啟用
- **WHEN** 選擇模式已啟用且選取至少一個任務
- **THEN** 啟用、停用、刪除三個批量操作按鈕 SHALL 為 enabled 狀態
