## ADDED Requirements

### Requirement: 目錄掃描 SHALL 過濾隱藏與系統目錄

目錄選擇器 SHALL 過濾掉名稱以 `.`、`#`、`@` 開頭的資料夾，這些通常是隱藏目錄或 NAS 系統目錄。

#### Scenario: 過濾 . 開頭目錄
- **WHEN** 目錄中包含 `.hidden` 資料夾
- **THEN** 該資料夾 SHALL 不出現在目錄列表中

#### Scenario: 過濾 # 開頭目錄
- **WHEN** 目錄中包含 `#recycle` 資料夾
- **THEN** 該資料夾 SHALL 不出現在目錄列表中

#### Scenario: 過濾 @ 開頭目錄
- **WHEN** 目錄中包含 `@eaDir` 資料夾
- **THEN** 該資料夾 SHALL 不出現在目錄列表中

#### Scenario: 正常目錄不被過濾
- **WHEN** 目錄中包含 `anime` 資料夾
- **THEN** 該資料夾 SHALL 出現在目錄列表中
