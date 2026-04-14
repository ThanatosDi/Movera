## Context

目前 Movera 的任務重新命名功能支援 Regex 與 Parse 兩種模式，可從檔案名稱解析出具名群組（如 `{episode}`、`{title}`），
再依據 dst_filename 模板產生新檔名。但當解析出的 episode 數值需要偏移（例如第二季 EP01 需轉為 EP13）時，
使用者只能手動在 dst_filename 中寫複雜的邏輯或逐一修改，無法自動化處理。

現行資料流：
1. 檔案下載完成 → Worker 取得 Task 設定
2. `Rename.execute_rename()` → 依 rule_type 分派至 `RegexRenameRule.rename()` 或 `ParseRenameRule.rename()`
3. 解析 src_filename 取得群組 → 套用 dst_filename 模板 → 產生新檔名

## Goals / Non-Goals

**Goals:**
- 讓使用者在任務設定中啟用 episode 偏移，選擇目標 group 並設定偏移量
- 後端在重新命名流程中自動將指定 group 的數值加上偏移量
- 前端在 TaskForm 中提供直覺的 UI 操作（開關、下拉選單、數字輸入）
- 資料庫透過 Alembic migration 新增必要欄位

**Non-Goals:**
- 不支援多個 group 同時偏移（僅單一 group）
- 不支援非數字 group 的偏移（如 title 等文字類 group）
- 不改變現有 preview API 的回應格式（偏移僅在實際重新命名時套用）
- 不支援數學運算式，僅支援固定偏移量（整數加減）

## Decisions

### 1. 資料模型：在 Task 上新增三個欄位

**決策**：在 Task model 新增 `episode_offset_enabled`（Boolean）、`episode_offset_group`（String）、`episode_offset_value`（Integer）三個欄位。

**理由**：偏移設定是任務層級的配置，與單一任務綁定。三個獨立欄位比 JSON 欄位更容易做 schema 驗證與查詢，且與現有欄位風格一致。

**替代方案**：
- JSON 欄位儲存：靈活但失去 schema 驗證，SQLite 的 JSON 支援也較弱。
- 獨立設定表：過度設計，偏移設定與 Task 強耦合。

**影響層級**：Model → Schema → Repository → Router

### 2. 偏移邏輯：在 rename 流程中注入偏移處理

**決策**：在 `Rename.execute_rename()` 中，於解析群組後、套用 dst_filename 前，對指定 group 的數值進行偏移。

**理由**：偏移是重新命名流程的一部分，放在 `Rename` 類別中最自然。修改 `execute_rename()` 而非各別 `rename()` 方法，可統一處理 regex 和 parse 兩種模式。

**替代方案**：
- 在各 RenameRule 子類別中分別處理：邏輯重複，不符合 DRY 原則。
- 在 Worker 層處理：破壞封裝，Worker 不應知道重新命名的內部邏輯。

**影響層級**：Service（rename utility）

### 3. 前端 Group 選項：從 Preview API 回應中取得

**決策**：前端在使用者填寫 src_filename 並觸發 preview 後，從 preview 回應的 groups 中取得可選的 group 名稱，作為下拉選單的選項。

**理由**：復用現有的 preview 機制，不需要額外的 API 端點。Groups 的來源與使用者定義的 src_filename 直接相關，preview 結果最準確。

**替代方案**：
- 新增專用 API 端點：增加維護成本，且 preview 已能提供相同資訊。
- 前端自行解析 pattern：容易與後端解析結果不一致。

**影響層級**：Component（TaskForm）→ Composable（useParsePreview / useRegexPreview）

### 4. 偏移量輸入：僅允許整數

**決策**：偏移量欄位使用 number input，限制為整數（可為正數或負數），後端以 Pydantic `int` 驗證。

**理由**：偏移量代表集數差距，一定是整數。允許負數以支援反向偏移的使用場景。

**影響層級**：Schema（前後端）→ Component

### 5. Episode 值支援小數：處理總集篇/番外

**決策**：episode group 值可能包含小數（如 `7.5`、`10.5`），代表總集篇或番外特別篇。偏移邏輯須能正確處理小數值，偏移後保留小數部分（如 `7.5` + 12 = `19.5`）。

**理由**：動畫命名慣例中 `.5` 集號常見於總集篇、番外或特別篇，偏移功能必須支援此場景。

**影響層級**：Service（rename utility）

### 6. 偏移結果格式保留：維持原始零填充

**決策**：偏移後的數值整數部分保持與原始 episode 整數部分相同的位數格式（如原始為 `01`，偏移 +12 後為 `13`；原始為 `07.5`，偏移 +12 後為 `19.5`）。

**理由**：檔案命名慣例通常使用固定位數（如兩位數），保留零填充可確保一致性。

**影響層級**：Service（rename utility）

## Risks / Trade-offs

- **[非數字 group 被選擇]** → 後端在偏移時檢查 group 值是否可轉為數字（整數或小數），若不可轉則跳過偏移並記錄警告日誌。
- **[偏移後數值為負數]** → 允許負數結果，但記錄警告日誌提醒使用者。實際命名是否合理由使用者自行判斷。
- **[已存在的任務升級]** → Migration 預設三個新欄位為 `enabled=False`、`group=None`、`value=0`，不影響現有行為。
- **[Preview 與實際重命名不一致]** → 此版本 preview 不顯示偏移效果（Non-Goal），使用者需理解偏移僅在實際執行時套用。未來可考慮在 preview 中加入偏移預覽。
