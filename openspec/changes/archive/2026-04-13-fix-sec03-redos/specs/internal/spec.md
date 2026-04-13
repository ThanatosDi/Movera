## ADDED Requirements

### Requirement: 正則表達式執行 SHALL 有逾時與長度保護

所有使用者提供的正則表達式 SHALL 在執行前進行長度檢查，且執行時 SHALL 有逾時保護，防止 ReDoS 攻擊。

#### Scenario: 正常正則表達式正常執行
- **WHEN** 使用者提供合法的正則表達式（如 `(.+) - (\d+).mp4`）
- **THEN** 系統 SHALL 正常編譯並執行匹配/替換，結果與原有行為一致

#### Scenario: 超長正則表達式被拒絕
- **WHEN** 使用者提供長度超過 500 字元的正則表達式
- **THEN** 系統 SHALL 拒絕編譯並拋出 ValueError

#### Scenario: 惡意正則表達式被逾時中斷
- **WHEN** 使用者提供會導致 catastrophic backtracking 的正則表達式（如 `(a+)+b`）
- **THEN** 系統 SHALL 在 3 秒內中斷執行並拋出 RegexTimeoutError
