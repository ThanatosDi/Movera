## Context

目前任務的 `src_filename` 和 `dst_filename` 規則需手動輸入。系統已有 parse 和 regex 兩種重新命名規則引擎，但沒有讓使用者儲存常用規則的機制。

現有相關元件：
- `backend/models/task.py` — Task model，含 `rename_rule`（parse/regex）、`src_filename`、`dst_filename`
- `backend/schemas.py` — Pydantic schemas，含 `ParsePreviewRequest`/`RegexPreviewRequest`
- `src/components/TaskForm.vue` — 任務表單，含規則輸入欄位
- `src/views/SettingView.vue` — 設定頁面，含 Tag 管理和允許目錄管理區塊

## Goals / Non-Goals

**Goals:**
- 建立常用規則資料模型與 CRUD API
- 在設定頁面提供管理常用規則的 UI
- 在任務表單的規則欄位旁提供快速套用常用規則的入口
- 套用時依據 `rename_rule`（parse/regex）和欄位類型（src/dst）篩選顯示

**Non-Goals:**
- 不實作規則的匯入/匯出功能
- 不實作規則的版本歷史
- 不自動偵測使用者輸入並建議常用規則
- 不支援規則的分組或分類（保持簡單）

## Decisions

### 1. 資料模型設計（Model 層）

新增 `PresetRule` 資料表：

| 欄位 | 型別 | 說明 |
|------|------|------|
| id | UUID (PK) | 唯一識別碼 |
| name | String (unique) | 規則名稱 |
| rule_type | String | 規則引擎類型：`parse` 或 `regex` |
| field_type | String | 對應欄位：`src` 或 `dst` |
| pattern | String | 規則內容（正規表達式或 parse 模板） |
| created_at | DateTime | 建立時間 |

**理由**: 將 `rule_type` 和 `field_type` 拆為獨立欄位，而非組合成單一欄位，方便前端依據兩個維度獨立篩選。不需要額外的關聯表。

**替代方案**: 使用 JSON 欄位儲存多組規則 — 但失去 SQL 查詢與篩選的便利性。

### 2. API 設計（Router 層）

端點前綴：`/api/v1/preset-rules`

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/api/v1/preset-rules` | 取得所有常用規則（支援 `rule_type` 和 `field_type` query 參數篩選） |
| POST | `/api/v1/preset-rules` | 建立常用規則 |
| PUT | `/api/v1/preset-rules/{id}` | 更新常用規則 |
| DELETE | `/api/v1/preset-rules/{id}` | 刪除常用規則 |

**理由**: 遵循現有 RESTful CRUD 模式（與 tag、task 一致）。GET 端點支援 query 參數篩選，前端 Modal 可直接請求對應類型的規則。

### 3. 設定頁面管理 UI（Component 層）

在 `SettingView.vue` 新增「常用規則」Card 區塊，位於 Tag 管理區塊之後。結構類似 Tag 管理：
- 列表顯示所有常用規則，每筆顯示名稱、規則類型 badge、欄位類型 badge、規則內容預覽
- 新增表單：名稱、規則類型選擇（parse/regex）、欄位類型選擇（src/dst）、規則內容
- 行內編輯與刪除

**理由**: 與現有設定區塊保持一致的 UX 模式，使用者無需學習新的操作方式。

### 4. 套用規則 Modal（Component 層）

在 `TaskForm.vue` 的 `src_filename` 和 `dst_filename` 輸入欄位旁新增按鈕圖示。點擊後開啟 `PresetRuleModal.vue`：
- Modal 接收 props：`ruleType`（parse/regex）、`fieldType`（src/dst）
- 從 API 取得篩選後的規則列表
- 使用者點擊規則後，emit 選中的 `pattern` 值
- 父元件收到後填入對應欄位

**理由**: 使用 Modal 而非下拉選單，因為規則內容可能較長，Modal 提供更充足的空間展示規則名稱與內容預覽。

### 5. 影響層級

| 層級 | 影響 |
|------|------|
| Model | 新增 `PresetRule` model |
| Migration | 新增 Alembic migration 建立 `preset_rules` 表 |
| Schema | 新增 `PresetRuleBase`、`PresetRuleCreate`、`PresetRuleUpdate`、`PresetRule` |
| Repository | 新增 `PresetRuleRepository` |
| Service | 新增 `PresetRuleService` |
| Router | 新增 `/api/v1/preset-rules` CRUD 端點 |
| Store | 新增 `presetRuleStore`（Pinia） |
| Component | 新增 `PresetRuleModal.vue`；修改 `TaskForm.vue`、`SettingView.vue` |
| i18n | 新增常用規則相關翻譯 key |

## Risks / Trade-offs

- **[設定頁面越來越長]** → 使用可收合的 Card 區塊緩解；未來可考慮將設定頁面拆分為 tabs
- **[規則名稱唯一性約束]** → 同 Tag 管理，名稱重複時後端回傳 409，前端顯示提示
- **[rename_rule 未選擇時無法套用]** → 套用按鈕僅在選擇 parse 或 regex 後才顯示，避免使用者困惑
