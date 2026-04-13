## Why

使用者在建立多個任務時，經常重複輸入相同的 `src_filename` 和 `dst_filename` 規則（如動畫命名慣例、電影字幕格式等）。目前每次都需手動輸入，既繁瑣又容易出錯。提供常用規則預設功能，可讓使用者一次建立、多次套用，大幅提升任務設定效率。

## What Changes

- 新增後端 `PresetRule` 資料表，儲存常用規則（名稱、規則類型 parse/regex、欄位類型 src/dst、規則內容）
- 新增完整的 `PresetRule` CRUD API（`/api/v1/preset-rules`）
- 在設定頁面新增「常用規則」管理區塊，可建立、編輯、刪除常用規則
- 在任務詳細頁面的 `src_filename` 和 `dst_filename` 輸入欄位旁新增「套用常用規則」按鈕
- 點擊按鈕後彈出 Modal，依據當前的 `rename_rule`（parse/regex）和欄位類型（src/dst）篩選顯示對應的常用規則
- 選擇規則後自動填入對應欄位

## Capabilities

### New Capabilities
- `preset-rule-management`: 常用規則的資料模型、CRUD API、設定頁面管理 UI
- `preset-rule-apply`: 任務編輯頁面中套用常用規則的 Modal 與互動邏輯

### Modified Capabilities

（無需修改現有 capability 的需求規格）

## Impact

- **後端**: 新增 Model、Schema、Repository、Service、Router（遵循現有分層架構）
- **資料庫**: 新增 `preset_rules` 資料表，需要 Alembic migration
- **前端元件**: 新增 `PresetRuleModal.vue`；修改 `SettingView.vue` 新增管理區塊；修改 `TaskForm.vue` 新增套用按鈕
- **狀態管理**: 新增 `presetRuleStore`（Pinia）
- **i18n**: 新增常用規則相關翻譯 key
- **API**: 新增 `/api/v1/preset-rules` CRUD 端點
