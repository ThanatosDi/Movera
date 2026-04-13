## Context

目前 Webhook 端點（`/webhook/on-complete`）接收 `filepath` 參數後直接傳入 Worker 處理，沒有驗證該路徑是否來自合法的下載目錄。這構成 SEC-02 資安漏洞：攻擊者可偽造 Webhook 請求對系統任意檔案執行搬移/重新命名。

現有架構中已有 `allowed_directories` 設定（用於前端目錄選擇器的存取控制），但該設定的用途是限制 UI 瀏覽範圍，與「檔案來源驗證」是不同的安全邊界。因此需要一個獨立的 `allowed_source_directories` 設定。

## Goals / Non-Goals

**Goals:**
- 新增 `allowed_source_directories` 設定項，讓管理者指定哪些目錄下的檔案允許被 Worker 處理
- 在設定頁面提供 UI 管理此白名單（與 `allowed_directories` 相同的操作模式）
- Worker 在執行任何檔案操作前驗證來源路徑
- 白名單為空時不阻擋任何路徑（向後相容）

**Non-Goals:**
- 不驗證 `move_to` 目標路徑（目標路徑由管理者透過任務設定控制，屬於不同安全邊界）
- 不新增 API 端點（使用既有的 `PUT /api/v1/settings` 批次更新）
- 不修改資料庫 schema（使用既有的 key-value 設定表）

## Decisions

### 1. 獨立設定項，不復用 `allowed_directories`

**選擇：** 新增 `allowed_source_directories` 設定，與 `allowed_directories` 分開管理。

**理由：** 兩者用途不同——`allowed_directories` 控制前端目錄瀏覽範圍，`allowed_source_directories` 控制 Webhook 檔案來源驗證。使用者可能希望 UI 瀏覽更多目錄（如目標資料夾），但只允許特定下載目錄作為來源。

**替代方案：** 復用 `allowed_directories` 同時作為來源驗證——被否決，因為會強制耦合兩個不同的安全策略。

### 2. 驗證邏輯放在 Worker 層（`process_completed_download`）

**選擇：** 在 `process_completed_download()` 函式的最前面執行路徑驗證，拒絕不在白名單內的路徑。

**理由：** 這是所有 Webhook 檔案操作的唯一入口點，在此驗證可以確保所有後續操作（match_task → rename → move）都受到保護。不需要修改 `move.py`（保持為純工具函式）。

**影響層級：** Service 層（`SettingService`）、Worker（`worker.py`）、`WorkerServices` dataclass。

### 3. 空白名單 = 允許全部（向後相容）

**選擇：** 當 `allowed_source_directories` 為空陣列或未設定時，不進行任何路徑限制。

**理由：** 既有使用者升級後不需要額外設定即可繼續正常運作。首次使用者也能先跑起來再配置。

### 4. 前端 UI 復用 `allowed_directories` 的操作模式

**選擇：** 在設定頁面新增一個 card 區塊，UI 交互模式與 `allowed_directories` 完全一致（輸入框 + 絕對路徑驗證 + 列表增刪）。

**理由：** 保持使用者體驗一致，降低學習成本。不需要新的 UI 元件。

**影響層級：** Component（`SettingView.vue`）、Store（`settingStore.ts`）、Schema、i18n。

### 5. 路徑驗證使用 `Path.resolve()` + `is_relative_to()`

**選擇：** 將使用者傳入的 filepath 與白名單路徑都做 `resolve()` 後，用 `is_relative_to()` 檢查。

**理由：** 可正確處理符號連結和相對路徑，防止透過 `../` 繞過白名單。

## Risks / Trade-offs

- **[風險] 白名單未設定時無保護** → 在 UI 上顯示提示文字，提醒使用者設定白名單以強化安全性
- **[風險] 路徑 resolve 在大量 symlink 場景下可能有效能影響** → 每次 Webhook 僅呼叫一次，影響可忽略
- **[取捨] 不驗證 move_to 目標路徑** → 目標路徑由管理者在任務中設定，若需要可在後續迭代中加入
