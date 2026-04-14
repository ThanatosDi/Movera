## ADDED Requirements

### Requirement: 啟用與停用 Episode 偏移

任務 SHALL 提供 episode 偏移開關設定。當 `episode_offset_enabled` 為 `false` 時，重新命名流程 MUST 與未新增此功能前的行為完全一致。

#### Scenario: 預設停用狀態

- **WHEN** 建立新任務時未指定 episode 偏移設定
- **THEN** `episode_offset_enabled` MUST 為 `false`，`episode_offset_group` MUST 為 `null`，`episode_offset_value` MUST 為 `0`

#### Scenario: 啟用 episode 偏移

- **WHEN** 使用者在任務設定中將 episode 偏移開關切換為啟用
- **THEN** 系統 MUST 顯示 group 選擇下拉選單與偏移量輸入欄位

#### Scenario: 停用 episode 偏移

- **WHEN** 使用者將 episode 偏移開關切換為停用
- **THEN** 系統 MUST 隱藏 group 選擇下拉選單與偏移量輸入欄位，但 MUST 保留先前設定的值（不清除）

### Requirement: 選擇偏移目標 Group

啟用 episode 偏移時，使用者 MUST 能從解析出的 group 中選擇一個作為偏移目標。

#### Scenario: Parse 模式下顯示 group 選項

- **WHEN** 任務的 rename_rule 為 `parse`，且 src_filename preview 成功解析出 groups
- **THEN** 下拉選單 MUST 列出所有解析出的具名 group（如 `title`、`episode`、`tags`）

#### Scenario: Regex 模式下顯示 group 選項

- **WHEN** 任務的 rename_rule 為 `regex`，且 src_filename preview 成功解析出 named groups
- **THEN** 下拉選單 MUST 列出所有解析出的具名 group（named groups）

#### Scenario: 無 preview 結果時

- **WHEN** 尚未觸發 preview 或 preview 未解析出任何 group
- **THEN** 下拉選單 MUST 顯示為空且不可選擇，並提示使用者先完成 src_filename 設定

#### Scenario: rename_rule 為 None 時

- **WHEN** 任務未選擇 rename_rule（值為 null）
- **THEN** episode 偏移區塊 MUST 不顯示（僅在有 rename_rule 時才顯示）

### Requirement: 設定偏移量

使用者 MUST 能設定一個整數偏移量，該值將在重新命名時加到選定 group 的數值上。

#### Scenario: 輸入正整數偏移量

- **WHEN** 使用者在偏移量欄位輸入 `12`
- **THEN** 系統 MUST 接受該值並儲存為整數 `12`

#### Scenario: 輸入負整數偏移量

- **WHEN** 使用者在偏移量欄位輸入 `-5`
- **THEN** 系統 MUST 接受該值並儲存為整數 `-5`

#### Scenario: 拒絕非數字輸入

- **WHEN** 使用者在偏移量欄位輸入非數字字元（如 `abc`、`1.5`）
- **THEN** 系統 MUST 阻止輸入或顯示驗證錯誤，不允許儲存非整數值

#### Scenario: 偏移量預設值

- **WHEN** 啟用 episode 偏移但未修改偏移量
- **THEN** 偏移量 MUST 預設為 `0`

### Requirement: 重新命名時套用偏移

當任務啟用 episode 偏移且設定有效時，重新命名流程 MUST 在產生新檔名前對指定 group 的數值進行偏移。

#### Scenario: Parse 模式正向偏移

- **WHEN** 任務的 rename_rule 為 `parse`，episode_offset_enabled 為 `true`，episode_offset_group 為 `episode`，episode_offset_value 為 `12`
- **AND** src_filename 解析出 `episode` 群組值為 `"01"`
- **THEN** 重新命名時 MUST 將 `episode` 值替換為 `"13"`（1 + 12 = 13，保持兩位數零填充）

#### Scenario: Regex 模式正向偏移

- **WHEN** 任務的 rename_rule 為 `regex`，episode_offset_enabled 為 `true`，episode_offset_group 為 `episode`，episode_offset_value 為 `12`
- **AND** src_filename 解析出 named group `episode` 值為 `"01"`
- **THEN** 重新命名時 MUST 將 `episode` 值替換為 `"13"`（1 + 12 = 13，保持兩位數零填充）

#### Scenario: 保持零填充格式

- **WHEN** 原始 group 值為 `"003"`，偏移量為 `10`
- **THEN** 偏移後的值 MUST 為 `"013"`（整數部分保持三位數零填充）

#### Scenario: 偏移後超出原始位數

- **WHEN** 原始 group 值為 `"99"`，偏移量為 `5`
- **THEN** 偏移後的值 MUST 為 `"104"`（超出兩位數時自然擴展，不截斷）

#### Scenario: 小數 episode 值偏移

- **WHEN** 原始 group 值為 `"07.5"`（總集篇/番外），偏移量為 `12`
- **THEN** 偏移後的值 MUST 為 `"19.5"`（整數部分 7 + 12 = 19，保持兩位數零填充，小數部分 `.5` 保留不變）

#### Scenario: 小數 episode 值零填充

- **WHEN** 原始 group 值為 `"7.5"`，偏移量為 `5`
- **THEN** 偏移後的值 MUST 為 `"12.5"`（整數部分 7 + 5 = 12，原始整數部分無零填充則結果也不填充）

#### Scenario: Group 值非數字時跳過偏移

- **WHEN** episode_offset_group 指定的 group 值不可轉為數字（如 `"abc"`，既非整數也非小數）
- **THEN** 系統 MUST 跳過偏移處理，使用原始值，並記錄警告日誌

#### Scenario: 偏移未啟用時不影響流程

- **WHEN** episode_offset_enabled 為 `false`
- **THEN** 重新命名流程 MUST 完全不受偏移設定影響，行為與無此功能時一致

### Requirement: API Schema 擴充

Task 的建立與更新 API MUST 支援 episode 偏移相關欄位。

#### Scenario: 建立任務時包含偏移設定

- **WHEN** POST `/api/v1/tasks` 請求包含 `episode_offset_enabled: true`、`episode_offset_group: "episode"`、`episode_offset_value: 12`
- **THEN** 系統 MUST 建立任務並儲存偏移設定

#### Scenario: 更新任務偏移設定

- **WHEN** PUT `/api/v1/tasks/{task_id}` 請求包含更新的偏移欄位
- **THEN** 系統 MUST 更新對應欄位並回傳更新後的完整任務資料

#### Scenario: API 回應包含偏移欄位

- **WHEN** GET `/api/v1/tasks/{task_id}` 回傳任務資料
- **THEN** 回應 MUST 包含 `episode_offset_enabled`、`episode_offset_group`、`episode_offset_value` 三個欄位

### Requirement: 資料庫 Migration

系統 MUST 透過 Alembic migration 新增 episode 偏移相關欄位，且不影響現有資料。

#### Scenario: 升級 Migration

- **WHEN** 執行 `alembic upgrade head`
- **THEN** task 表 MUST 新增 `episode_offset_enabled`（Boolean, 預設 false）、`episode_offset_group`（String, nullable）、`episode_offset_value`（Integer, 預設 0）三個欄位

#### Scenario: 降級 Migration

- **WHEN** 執行 `alembic downgrade` 至此 migration 之前的版本
- **THEN** task 表 MUST 移除上述三個欄位
