## Why

目前 Movera 的重新命名功能（Regex/Parse）可以解析出 episode 等群組，但無法對 episode 數值進行偏移調整。
當使用者下載的影片 episode 編號與實際需要的編號不一致時（例如第二季從 EP01 開始，但使用者希望接續第一季的編號），
需要手動修改每個檔案的命名規則，非常不便。新增 episode 偏移功能可以讓使用者直接設定偏移量，自動調整 episode 數值。

## What Changes

- 在任務詳細頁（TaskForm）中新增「Episode 偏移」設定區塊
- 新增開關（Switch）控制是否啟用 episode 偏移功能
- 啟用時顯示下拉選單，列出從 src_filename 解析出的所有 group，讓使用者選擇哪個 group 作為 episode
- 提供數字輸入欄位讓使用者設定偏移量（僅允許整數，可為正負值）
- 後端在執行重新命名時，若啟用偏移，將選定 group 的數值加上偏移量後再套用到 dst_filename
- 資料庫新增欄位儲存 episode 偏移設定（啟用狀態、目標 group、偏移量）

## Capabilities

### New Capabilities

- `episode-offset`: 在任務中設定 episode 偏移功能，包含啟用開關、group 選擇、偏移量設定，以及重新命名時的數值偏移計算邏輯

### Modified Capabilities

<!-- 無需修改現有 spec 層級的行為 -->

## Impact

- **Backend**: 
  - `backend/models/task.py` — Task model 新增 episode 偏移相關欄位
  - `backend/schemas.py` — Pydantic schema 新增對應欄位
  - `backend/utils/rename.py` — RegexRenameRule 與 ParseRenameRule 新增偏移邏輯
  - `migration/` — 新增 Alembic migration 腳本
- **Frontend**:
  - `src/components/TaskForm.vue` — 新增 episode 偏移 UI 區塊
  - `src/schemas/index.ts` — 更新前端 schema
  - `src/locales/` — 新增 i18n 翻譯鍵值
- **API**: `PUT /api/v1/tasks/{task_id}` 與 `POST /api/v1/tasks` 的請求/回應 schema 擴充
