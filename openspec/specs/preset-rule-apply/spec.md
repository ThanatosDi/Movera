## ADDED Requirements

### Requirement: 任務表單顯示套用常用規則按鈕
當任務的 `rename_rule` 已選擇（parse 或 regex）時，`src_filename` 和 `dst_filename` 輸入欄位旁 SHALL 顯示「套用常用規則」按鈕。當 `rename_rule` 未選擇時，按鈕 SHALL 隱藏。

#### Scenario: rename_rule 已選擇時顯示按鈕
- **WHEN** 使用者選擇 `rename_rule` 為 `parse` 或 `regex`
- **THEN** `src_filename` 和 `dst_filename` 欄位旁各顯示一個「套用常用規則」按鈕

#### Scenario: rename_rule 未選擇時隱藏按鈕
- **WHEN** `rename_rule` 為 null（未選擇重新命名規則）
- **THEN** 不顯示「套用常用規則」按鈕

### Requirement: 點擊按鈕開啟常用規則 Modal
使用者點擊「套用常用規則」按鈕後，系統 SHALL 開啟 Modal，顯示與當前 `rename_rule` 和欄位類型對應的常用規則列表。

#### Scenario: 從 src_filename 開啟 Modal
- **WHEN** 使用者在 `src_filename` 欄位旁點擊按鈕，且 `rename_rule` 為 `parse`
- **THEN** Modal 開啟，顯示 `rule_type=parse` 且 `field_type=src` 的常用規則

#### Scenario: 從 dst_filename 開啟 Modal
- **WHEN** 使用者在 `dst_filename` 欄位旁點擊按鈕，且 `rename_rule` 為 `regex`
- **THEN** Modal 開啟，顯示 `rule_type=regex` 且 `field_type=dst` 的常用規則

#### Scenario: 無對應規則時顯示空狀態
- **WHEN** Modal 開啟但沒有符合條件的常用規則
- **THEN** Modal 中顯示「尚無對應的常用規則」提示，並引導至設定頁面新增

### Requirement: 選擇規則後填入欄位
使用者在 Modal 中選擇一筆常用規則後，系統 SHALL 將該規則的 `pattern` 填入對應的輸入欄位，並關閉 Modal。

#### Scenario: 選擇規則並套用
- **WHEN** 使用者在 Modal 中點擊一筆常用規則
- **THEN** 該規則的 `pattern` 值填入對應的 `src_filename` 或 `dst_filename` 欄位，Modal 關閉

#### Scenario: 套用規則覆蓋現有值
- **WHEN** 欄位已有內容，使用者選擇一筆常用規則
- **THEN** 欄位內容被替換為選擇的規則 `pattern`
