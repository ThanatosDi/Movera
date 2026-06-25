## ADDED Requirements

### Requirement: 管理員帳號儲存
系統 SHALL 以單一管理員帳號模式運作，帳號資料（使用者名稱、密碼雜湊、salt）儲存於 SQLite。密碼 MUST 以前端傳入的 SHA-256 值再加上每帳號隨機 salt 進行雜湊後儲存，且系統 MUST NOT 以明文形式儲存或記錄密碼。

#### Scenario: 建立帳號時儲存雜湊
- **WHEN** 系統建立管理員帳號並收到前端傳來的 `sha256(password)`
- **THEN** 系統產生隨機 salt，計算 `sha256(salt + 收到的值)` 並連同 salt 儲存於 SQLite，不儲存任何明文密碼

#### Scenario: 拒絕明文密碼儲存
- **WHEN** 檢視 SQLite 中的帳號資料
- **THEN** 僅存在密碼雜湊與 salt，不存在明文密碼或可逆的密碼表示

### Requirement: 透過環境變數預設帳號密碼
系統 SHALL 支援以環境變數 `MOVERA_ADMIN_USERNAME` 與 `MOVERA_ADMIN_PASSWORD` 預設管理員帳號。當資料庫尚無任何帳號且兩個環境變數皆有設定時，系統 MUST 於首次啟動建立該帳號。

#### Scenario: 首次啟動以 env 建立帳號
- **WHEN** 資料庫無任何管理員帳號，且 `MOVERA_ADMIN_USERNAME` 與 `MOVERA_ADMIN_PASSWORD` 皆已設定
- **THEN** 系統於啟動時建立對應帳號，並以加 salt 的 SHA-256 儲存密碼雜湊

#### Scenario: 已有帳號時不覆寫
- **WHEN** 資料庫已存在管理員帳號
- **THEN** 系統忽略環境變數預設值，不覆寫既有帳號

### Requirement: 登入頁面與前端密碼雜湊
系統 SHALL 提供登入頁面，包含使用者名稱與密碼輸入欄位。前端 MUST 先以 SHA-256 雜湊密碼，再以該雜湊值 POST 至後端，MUST NOT 傳送明文密碼。

#### Scenario: 成功登入
- **WHEN** 使用者於登入頁輸入正確的使用者名稱與密碼並送出
- **THEN** 前端送出 `sha256(password)`，後端比對成功並回傳 JWT，前端導向主畫面

#### Scenario: 帳號或密碼錯誤
- **WHEN** 使用者輸入錯誤的使用者名稱或密碼
- **THEN** 後端回傳 401，前端顯示登入失敗訊息且不發放 token

#### Scenario: 不傳送明文密碼
- **WHEN** 觀察登入請求的 payload
- **THEN** payload 僅含使用者名稱與 SHA-256 後的密碼值，不含明文密碼

### Requirement: 登入後簽發 JWT
登入成功後，系統 SHALL 以 HMAC secret 採 HS256 演算法簽發 JWT，內容 MUST 包含使用者識別與過期時間（`exp`）。

#### Scenario: 簽發具過期時間的 token
- **WHEN** 使用者登入成功
- **THEN** 系統回傳以 HS256 簽章、含 `sub` 與 `exp` claim 的 JWT

#### Scenario: 前端登出清除 token
- **WHEN** 使用者登出
- **THEN** 前端清除已儲存的 JWT，後續 `/api/v1/*` 請求不再附帶該 token
