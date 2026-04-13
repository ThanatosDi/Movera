## ADDED Requirements

### Requirement: 格式字串替換 SHALL 禁止屬性存取

使用者提供的格式字串 SHALL 僅支援 `{key}` 簡單替換，不允許 `{key.attr}`、`{key[0]}` 等進階語法。

#### Scenario: 正常 {key} 替換
- **WHEN** 格式字串為 `{title} - S01E{episode}.mp4`，mapping 為 `{"title": "動畫", "episode": "01"}`
- **THEN** 結果 SHALL 為 `動畫 - S01E01.mp4`

#### Scenario: 屬性存取語法被忽略
- **WHEN** 格式字串包含 `{title.__class__}`
- **THEN** 系統 SHALL 保留原始佔位符 `{title.__class__}` 不替換（或拋出錯誤）

#### Scenario: 未匹配的 key 保留原始佔位符
- **WHEN** 格式字串包含 `{unknown_key}`，但 mapping 中沒有該 key
- **THEN** 系統 SHALL 保留原始佔位符 `{unknown_key}`
