## ADDED Requirements

### Requirement: CORS SHALL 僅允許必要的 HTTP 方法與標頭

CORS middleware SHALL 明確列舉允許的 HTTP 方法和請求標頭，不使用萬用字元。

#### Scenario: 允許的 HTTP 方法
- **WHEN** 前端發送 GET、POST、PUT、DELETE 請求
- **THEN** CORS SHALL 允許通過

#### Scenario: 不允許的 HTTP 方法
- **WHEN** 外部發送 PATCH、OPTIONS（非預檢）等未列舉的方法
- **THEN** CORS SHALL 拒絕

---

### Requirement: Settings API SHALL 僅接受白名單內的 key

`PUT /api/v1/settings` SHALL 過濾掉不在白名單內的設定 key，僅處理已知的合法 key。

#### Scenario: 合法 key 正常更新
- **WHEN** 請求包含 `{"timezone": "UTC", "locale": "en"}`
- **THEN** 系統 SHALL 正常更新這些設定

#### Scenario: 未知 key 被忽略
- **WHEN** 請求包含 `{"timezone": "UTC", "malicious_key": "value"}`
- **THEN** 系統 SHALL 更新 `timezone`，忽略 `malicious_key`
