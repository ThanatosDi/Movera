## Context

目前設定頁面有兩種操作模式：
1. **即時保存**：常用規則、標籤 — 操作後直接呼叫各自的 CRUD API，顯示通知
2. **批次保存**：允許目錄、來源白名單、一般設定 — 修改本地 state，點「儲存設定」統一提交

這兩種模式的不一致造成使用者困惑。本變更將目錄相關操作統一為即時保存模式。

## Goals / Non-Goals

**Goals:**
- `addDirectory` / `removeDirectory` / `addSourceDirectory` / `removeSourceDirectory` 改為 async，操作後立即呼叫 `settingStore.updateSettings()` 保存
- 保存成功/失敗時顯示通知（與常用規則一致）
- 一般設定（語言、時區）仍保留「儲存設定」按鈕（因為它們不是列表操作）

**Non-Goals:**
- 不修改後端 API
- 不改變常用規則和標籤的操作邏輯

## Decisions

### 1. 使用既有的 `settingStore.updateSettings()` 而非新增專用 API

**選擇：** 在 add/remove 操作後，將完整的 settings 物件透過 `PUT /api/v1/settings` 提交。

**理由：** 後端已有此 API，不需要新增端點。目錄操作本質上就是修改 settings 的一部分。

### 2. 保留一般設定的「儲存設定」按鈕

**選擇：** 「儲存設定」按鈕保留，但僅用於一般設定（語言、時區）。

**理由：** 語言和時區是單值欄位，不適合每次 input change 就保存。保留按鈕符合表單慣例。

### 3. 操作失敗時回滾本地狀態

**選擇：** 如果 API 呼叫失敗，將本地 state 恢復到操作前的狀態。

**理由：** 避免 UI 與伺服器狀態不一致。

## Risks / Trade-offs

- **[風險] 快速連續操作可能導致競態條件** → 每次操作都送出完整 settings，最後一次成功的操作會是最終狀態，可接受
- **[取捨] 每次操作都呼叫 API 增加請求次數** → 目錄操作頻率很低，影響可忽略
