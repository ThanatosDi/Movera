## ADDED Requirements

### Requirement: SPA 路由路徑穿越防護
SPA catch-all 路由 `/{full_path:path}` SHALL 在提供靜態檔案前，以 `Path.resolve()` 正規化路徑並以 `is_relative_to()` 驗證結果仍在 `DIST_DIR` 之下。不在 `DIST_DIR` 範圍內的路徑 SHALL 回傳 `index.html`（SPA fallback）而非目標檔案。

#### Scenario: 正常靜態檔案存取
- **WHEN** 使用者請求 `GET /favicon.ico` 且該檔案存在於 `DIST_DIR` 下
- **THEN** 系統 SHALL 回傳該靜態檔案

#### Scenario: 路徑穿越攻擊被阻擋
- **WHEN** 攻擊者請求 `GET /../../etc/passwd` 或含 `..` 的路徑
- **THEN** 解析後路徑不在 `DIST_DIR` 範圍內，系統 SHALL 回傳 `index.html`（SPA fallback）

### Requirement: Webhook filepath 路徑驗證
Webhook worker 在處理 `filepath` 前 SHALL 以 `Path.resolve()` 正規化路徑並驗證其為有效的現存檔案。系統 SHALL 記錄警告日誌並跳過不合法的路徑。

#### Scenario: 合法的檔案路徑
- **WHEN** Webhook 收到 filepath `/downloads/anime/episode01.mkv` 且該檔案存在
- **THEN** 系統 SHALL 正常處理該檔案

#### Scenario: 路徑穿越嘗試被拒絕
- **WHEN** Webhook 收到 filepath `/../etc/passwd`
- **THEN** 系統 SHALL 記錄警告日誌並拒絕處理，不執行任何檔案操作

#### Scenario: 不存在的檔案路徑
- **WHEN** Webhook 收到 filepath 指向不存在的檔案
- **THEN** 系統 SHALL 記錄警告日誌並跳過處理

### Requirement: Task move_to 路徑白名單驗證
Task 建立與更新時，`move_to` 路徑 SHALL 經過 `Path.resolve()` 正規化，並驗證其位於 `allowed_directories` 設定的白名單目錄內（或其子目錄）。不在白名單內的路徑 SHALL 被拒絕。

#### Scenario: move_to 在白名單目錄內
- **WHEN** 使用者建立任務且 `move_to` 為 `/downloads/anime/show1`，而 `/downloads` 在 `allowed_directories` 中
- **THEN** 系統 SHALL 接受該路徑並建立任務

#### Scenario: move_to 不在白名單目錄內
- **WHEN** 使用者建立任務且 `move_to` 為 `/etc/cron.d/evil`，而該路徑不在任何 `allowed_directories` 內
- **THEN** 系統 SHALL 回傳 HTTP 400/422 錯誤，拒絕建立任務

#### Scenario: move_to 路徑穿越嘗試
- **WHEN** 使用者建立任務且 `move_to` 為 `/downloads/../etc/passwd`
- **THEN** 系統 SHALL 在 resolve 後發現路徑不在白名單內，拒絕建立任務

### Requirement: Rename 產出檔名路徑穿越防護
Rename 工具（`ParseRenameRule` 和 `RegexRenameRule`）在執行重新命名前 SHALL 驗證產出的檔名不含路徑分隔符（`/`、`\`）或 `..` 序列。含有這些字元的產出 SHALL 引發錯誤而非執行重新命名。

#### Scenario: 正常的檔名重新命名
- **WHEN** rename pattern 產出 `Episode 01.mkv`
- **THEN** 系統 SHALL 正常執行重新命名

#### Scenario: 產出含路徑穿越的檔名
- **WHEN** rename dst pattern 產出 `../../etc/cron.d/evil`
- **THEN** 系統 SHALL 拒絕執行重新命名並引發錯誤

#### Scenario: 產出含路徑分隔符的檔名
- **WHEN** rename dst pattern 產出 `subdir/file.mkv`（含 `/`）
- **THEN** 系統 SHALL 拒絕執行重新命名並引發錯誤

### Requirement: .dockerignore 檔案
專案根目錄 SHALL 包含 `.dockerignore` 檔案，排除 `.git/`、`.env*`、`node_modules/`、`tests/`、`__pycache__/`、`.vscode/`、`openspec/`、`*.md`（README 除外）等非必要檔案，防止敏感資訊或開發檔案進入 Docker 映像檔。

#### Scenario: Docker 建置排除敏感檔案
- **WHEN** 執行 `docker build` 且專案根目錄存在 `.env` 檔案
- **THEN** `.env` 檔案 SHALL 不被複製進映像檔
