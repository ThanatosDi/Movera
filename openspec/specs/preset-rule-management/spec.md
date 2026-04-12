## ADDED Requirements

### Requirement: 常用規則資料模型
系統 SHALL 提供 `preset_rules` 資料表，每筆常用規則 SHALL 包含：唯一識別碼（UUID）、名稱（唯一）、規則類型（`parse` 或 `regex`）、欄位類型（`src` 或 `dst`）、規則內容（pattern）、建立時間。

#### Scenario: 資料表結構正確
- **WHEN** 資料庫遷移完成
- **THEN** `preset_rules` 資料表包含 `id`、`name`、`rule_type`、`field_type`、`pattern`、`created_at` 欄位

### Requirement: 常用規則 CRUD API
系統 SHALL 提供 `/api/v1/preset-rules` RESTful CRUD 端點。GET 端點 SHALL 支援 `rule_type` 和 `field_type` query 參數篩選。

#### Scenario: 取得所有常用規則
- **WHEN** 發送 `GET /api/v1/preset-rules`
- **THEN** 回傳所有常用規則的 JSON 陣列，HTTP 200

#### Scenario: 依規則類型篩選
- **WHEN** 發送 `GET /api/v1/preset-rules?rule_type=parse`
- **THEN** 僅回傳 `rule_type` 為 `parse` 的常用規則

#### Scenario: 依欄位類型篩選
- **WHEN** 發送 `GET /api/v1/preset-rules?field_type=src`
- **THEN** 僅回傳 `field_type` 為 `src` 的常用規則

#### Scenario: 同時篩選規則類型和欄位類型
- **WHEN** 發送 `GET /api/v1/preset-rules?rule_type=regex&field_type=dst`
- **THEN** 僅回傳 `rule_type` 為 `regex` 且 `field_type` 為 `dst` 的常用規則

#### Scenario: 建立常用規則
- **WHEN** 發送 `POST /api/v1/preset-rules`，body 包含有效的名稱、規則類型、欄位類型、規則內容
- **THEN** 建立成功，回傳新建的常用規則，HTTP 201

#### Scenario: 建立重複名稱的常用規則
- **WHEN** 發送 `POST /api/v1/preset-rules`，body 中的名稱已存在
- **THEN** 回傳 HTTP 409，包含錯誤訊息

#### Scenario: 建立無效規則類型的常用規則
- **WHEN** 發送 `POST /api/v1/preset-rules`，`rule_type` 不是 `parse` 或 `regex`
- **THEN** 回傳 HTTP 422，包含驗證錯誤

#### Scenario: 建立無效欄位類型的常用規則
- **WHEN** 發送 `POST /api/v1/preset-rules`，`field_type` 不是 `src` 或 `dst`
- **THEN** 回傳 HTTP 422，包含驗證錯誤

#### Scenario: 更新常用規則
- **WHEN** 發送 `PUT /api/v1/preset-rules/{id}`，body 包含更新的欄位
- **THEN** 更新成功，回傳更新後的常用規則，HTTP 200

#### Scenario: 更新不存在的常用規則
- **WHEN** 發送 `PUT /api/v1/preset-rules/{id}`，該 ID 不存在
- **THEN** 回傳 HTTP 404

#### Scenario: 刪除常用規則
- **WHEN** 發送 `DELETE /api/v1/preset-rules/{id}`
- **THEN** 刪除成功，HTTP 204

#### Scenario: 刪除不存在的常用規則
- **WHEN** 發送 `DELETE /api/v1/preset-rules/{id}`，該 ID 不存在
- **THEN** 回傳 HTTP 404

### Requirement: 設定頁面常用規則管理區塊
系統 SHALL 在設定頁面新增「常用規則」管理區塊，使用者 SHALL 能在此建立、檢視、編輯和刪除常用規則。

#### Scenario: 顯示常用規則列表
- **WHEN** 使用者進入設定頁面
- **THEN** 「常用規則」區塊顯示所有已建立的常用規則，每筆顯示名稱、規則類型（parse/regex）、欄位類型（src/dst）、規則內容

#### Scenario: 無常用規則時顯示空狀態
- **WHEN** 系統中無任何常用規則
- **THEN** 顯示「尚未建立任何常用規則」提示文字

#### Scenario: 新增常用規則
- **WHEN** 使用者填寫名稱、選擇規則類型、選擇欄位類型、輸入規則內容並點擊新增
- **THEN** 常用規則建立成功，即時顯示在列表中

#### Scenario: 刪除常用規則
- **WHEN** 使用者點擊某筆常用規則的刪除按鈕並確認
- **THEN** 該常用規則從列表中移除
