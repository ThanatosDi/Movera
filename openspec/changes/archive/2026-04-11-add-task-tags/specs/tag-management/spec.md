## ADDED Requirements

### Requirement: Tag 資料模型
系統 SHALL 維護一個獨立的 Tag 資料表，每個標籤包含唯一 ID、名稱與顏色屬性。

#### Scenario: Tag 表結構
- **WHEN** 檢查 `tag` 資料表
- **THEN** SHALL 包含 `id`（UUID, PK）、`name`（String, unique, not null）、`color`（String, not null）欄位

#### Scenario: Tag 名稱唯一性
- **WHEN** 嘗試建立名稱與既有標籤相同的新標籤
- **THEN** 系統 SHALL 回傳 409 Conflict 錯誤

### Requirement: Tag CRUD API
系統 SHALL 提供完整的 Tag CRUD REST API，路徑前綴為 `/api/v1/tags`。

#### Scenario: 列出所有標籤
- **WHEN** 發送 `GET /api/v1/tags`
- **THEN** SHALL 回傳所有標籤的陣列，每個標籤包含 `id`、`name`、`color` 欄位

#### Scenario: 建立標籤
- **WHEN** 發送 `POST /api/v1/tags`，body 包含 `{ "name": "動畫", "color": "blue" }`
- **THEN** SHALL 建立標籤並回傳完整標籤物件，HTTP 201

#### Scenario: 更新標籤
- **WHEN** 發送 `PUT /api/v1/tags/{tag_id}`，body 包含 `{ "name": "新名稱", "color": "red" }`
- **THEN** SHALL 更新標籤並回傳更新後的標籤物件

#### Scenario: 刪除標籤
- **WHEN** 發送 `DELETE /api/v1/tags/{tag_id}`
- **THEN** SHALL 刪除標籤，回傳 HTTP 204
- **THEN** 與該標籤關聯的所有 task_tags 記錄 SHALL 自動清除

### Requirement: Tag 顏色為預定義色票
標籤顏色 SHALL 限制為預定義的色票名稱集合，不接受任意 hex 值。

#### Scenario: 合法顏色值
- **WHEN** 建立或更新標籤時提供 `color` 值為 `"red"`, `"orange"`, `"yellow"`, `"green"`, `"blue"`, `"purple"`, `"pink"`, `"gray"` 之一
- **THEN** SHALL 成功建立或更新

#### Scenario: 非法顏色值
- **WHEN** 建立或更新標籤時提供 `color` 值不在預定義色票中
- **THEN** SHALL 回傳 422 Validation Error

### Requirement: Setting 頁面標籤管理介面
Setting 頁面 SHALL 包含「標籤管理」區塊，提供新增、編輯、刪除標籤的 UI 操作。

#### Scenario: 顯示標籤列表
- **WHEN** 開啟 Setting 頁面
- **THEN** SHALL 顯示所有既有標籤，每個標籤以彩色 Badge 形式呈現

#### Scenario: 新增標籤
- **WHEN** 在標籤管理區塊輸入標籤名稱並選擇顏色後點擊新增
- **THEN** SHALL 建立新標籤並更新列表

#### Scenario: 編輯標籤
- **WHEN** 點擊標籤的編輯按鈕
- **THEN** SHALL 可修改標籤名稱與顏色

#### Scenario: 刪除標籤
- **WHEN** 點擊標籤的刪除按鈕並確認
- **THEN** SHALL 刪除標籤並從列表中移除
