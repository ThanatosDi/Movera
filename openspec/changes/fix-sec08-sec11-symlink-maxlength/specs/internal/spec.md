## ADDED Requirements

### Requirement: 目錄掃描 SHALL 跳過符號連結

目錄瀏覽服務在列舉子目錄時 SHALL 跳過 symlink，防止透過符號連結繞過存取控制。

#### Scenario: symlink 被排除
- **WHEN** 允許目錄中包含指向外部路徑的 symlink
- **THEN** 該 symlink SHALL 不出現在目錄列表中

#### Scenario: 正常目錄不受影響
- **WHEN** 允許目錄中包含正常的子目錄
- **THEN** 該子目錄 SHALL 正常出現在目錄列表中

---

### Requirement: Pydantic schema 的 str 欄位 SHALL 有 max_length 限制

所有使用者輸入的字串欄位 SHALL 定義合理的 `max_length`，超過限制時 Pydantic 驗證 SHALL 回傳 422 錯誤。

#### Scenario: 正常長度的輸入通過驗證
- **WHEN** 使用者輸入長度在限制內的字串
- **THEN** 系統 SHALL 正常接受

#### Scenario: 超長輸入被拒絕
- **WHEN** 使用者輸入超過 max_length 的字串
- **THEN** 系統 SHALL 回傳 422 驗證錯誤
