## ADDED Requirements

### Requirement: 全域未預期錯誤攔截器
系統 SHALL 新增全域 `Exception` handler，攔截所有未被其他 handler 捕捉的錯誤。對外 SHALL 回傳 HTTP 500 與固定 body `{"detail": "Internal Server Error"}`，並以 loguru 記錄完整的錯誤堆疊。

#### Scenario: 未預期例外被攔截
- **WHEN** 任何端點拋出未被明確處理的 Exception
- **THEN** 系統 SHALL 回傳 HTTP 500 `{"detail": "Internal Server Error"}`，且伺服器日誌包含完整堆疊追蹤

#### Scenario: 已處理例外不受影響
- **WHEN** 端點拋出已註冊的例外（如 TaskNotFound）
- **THEN** 系統 SHALL 依照原有 handler 回傳對應的 HTTP 狀態碼與訊息，不受全域 handler 影響

### Requirement: 錯誤訊息不洩漏內部路徑
Directory 相關例外的 HTTP 回應 SHALL 不包含伺服器檔案系統的完整路徑。對外回傳的錯誤訊息 SHALL 使用通用描述（如「目錄不存在」、「無權存取此目錄」），完整路徑僅記錄在伺服器端日誌中。

#### Scenario: DirectoryNotFound 不洩漏路徑
- **WHEN** 使用者請求不存在的目錄
- **THEN** HTTP 回應的 detail SHALL 為通用訊息（不含完整路徑），伺服器日誌 SHALL 包含完整路徑

#### Scenario: DirectoryAccessDenied 不洩漏路徑
- **WHEN** 使用者請求無權存取的目錄
- **THEN** HTTP 回應的 detail SHALL 為通用訊息（不含完整路徑），伺服器日誌 SHALL 包含完整路徑

### Requirement: CORS 配置收緊
CORS 中介層 SHALL 明確列出允許的 HTTP methods（`GET`、`POST`、`PUT`、`DELETE`、`OPTIONS`）和 headers（`Content-Type`、`Authorization`、`X-API-Key`），不使用萬用字元 `*`。

#### Scenario: 允許的 method 通過 CORS
- **WHEN** 瀏覽器發送 `GET` 或 `POST` 的 preflight 請求
- **THEN** CORS 回應 SHALL 包含該 method 在 `Access-Control-Allow-Methods` 中

#### Scenario: 不允許的 method 被 CORS 拒絕
- **WHEN** 瀏覽器發送 `PATCH` 的 preflight 請求
- **THEN** CORS 回應 SHALL 不包含 `PATCH` 在 `Access-Control-Allow-Methods` 中

### Requirement: Settings API 輸入驗證
`PUT /api/v1/settings` 端點 SHALL 使用明確的 Pydantic schema 驗證請求 body，僅接受白名單欄位。非白名單欄位 SHALL 被忽略或引發驗證錯誤。

#### Scenario: 合法的設定更新
- **WHEN** 使用者送出 `{"allowed_directories": ["/downloads"]}` 至 `PUT /settings`
- **THEN** 系統 SHALL 接受並更新設定

#### Scenario: 非白名單欄位被拒絕
- **WHEN** 使用者送出包含非白名單欄位的請求
- **THEN** 系統 SHALL 忽略非白名單欄位或回傳 422 驗證錯誤

### Requirement: Schema 字串欄位長度限制
所有使用者可輸入的字串欄位 SHALL 設定合理的 `max_length` 限制：名稱欄位 MUST 不超過 255 字元，路徑與 pattern 欄位 MUST 不超過 1024 字元。

#### Scenario: 超過長度限制的輸入被拒絕
- **WHEN** 使用者建立任務且 `name` 欄位超過 255 字元
- **THEN** 系統 SHALL 回傳 HTTP 422 驗證錯誤

#### Scenario: 正常長度的輸入被接受
- **WHEN** 使用者建立任務且所有欄位長度在限制內
- **THEN** 系統 SHALL 正常接受並建立任務

### Requirement: 前端通知系統移除 innerHTML 渲染路徑
前端 `useNotification` composable SHALL 移除 `html` 選項與 `innerHTML` 渲染路徑。所有通知描述 SHALL 僅以純文字方式渲染。

#### Scenario: 通知僅渲染純文字
- **WHEN** 呼叫 `useNotification.showSuccess(title, description)`
- **THEN** description SHALL 以純文字渲染，不支援 HTML 標記

### Requirement: Trivy CI 掃描阻擋高危漏洞
Trivy CI 掃描工作流 SHALL 設定 `exit-code: 1`，當發現 CRITICAL 或 HIGH 級別漏洞時 SHALL 中斷建置流程。

#### Scenario: 無漏洞時建置通過
- **WHEN** Trivy 掃描未發現 CRITICAL 或 HIGH 漏洞
- **THEN** CI 建置 SHALL 正常通過

#### Scenario: 發現高危漏洞時建置失敗
- **WHEN** Trivy 掃描發現 CRITICAL 級別漏洞
- **THEN** CI 建置 SHALL 失敗並回報漏洞資訊

### Requirement: 外部連結安全屬性
所有前端元件中以 `target="_blank"` 開啟的外部連結 SHALL 包含 `rel="noopener noreferrer"` 屬性。

#### Scenario: 外部連結包含安全屬性
- **WHEN** Vue 元件渲染含 `target="_blank"` 的 `<a>` 標籤
- **THEN** 該標籤 SHALL 同時包含 `rel="noopener noreferrer"` 屬性
