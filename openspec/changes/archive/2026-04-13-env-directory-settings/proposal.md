## Why

目前 `allowed_directories` 和 `allowed_source_directories` 只能透過 Web UI 設定，在 Docker 部署環境中無法透過環境變數預先配置。這導致管理者每次重新部署都需手動設定，且無法透過 docker-compose.yml 集中管理安全策略。此外，缺乏鎖定機制讓容器化部署中的安全設定可能被前端使用者意外修改或刪除。

## What Changes

- 新增環境變數 `ALLOWED_DIRECTORIES`（逗號分隔的絕對路徑清單），啟動時自動合併至資料庫設定
- 新增環境變數 `ALLOWED_SOURCE_DIRECTORIES`（逗號分隔的絕對路徑清單），啟動時自動合併至資料庫設定
- 透過環境變數注入的路徑項目在 UI 中標示為「環境變數鎖定」，不可被刪除
- 新增環境變數 `ALLOW_WEBUI_SETTING`（預設 `true`），設為 `false` 時：
  - 前端 UI 隱藏 `allowed_directories` 和 `allowed_source_directories` 的新增輸入框
  - **BREAKING** `PUT /api/v1/settings` API 拒絕修改 `allowed_directories` 和 `allowed_source_directories` 欄位，回傳 403

## Capabilities

### New Capabilities
- `env-directory-config`: 透過環境變數設定目錄白名單，涵蓋環境變數解析、啟動時資料庫合併、鎖定項目不可刪除、`ALLOW_WEBUI_SETTING` 開關控制

### Modified Capabilities
- `source-path-whitelist`: UI 的新增/刪除行為受 `ALLOW_WEBUI_SETTING` 控制，環境變數項目不可刪除

## Impact

- **後端**：`SettingService`（啟動時合併環境變數、鎖定項目保護）、`setting` router（API 層 403 攔截）、`backend.py`（lifespan 啟動注入）
- **前端**：`SettingView.vue`（鎖定項目 UI、條件隱藏新增輸入框）、`settingStore.ts`（新增鎖定狀態欄位）、Settings schema
- **API**：`GET /api/v1/settings` 回傳結構需包含哪些項目來自環境變數；`PUT /api/v1/settings` 新增 403 回應
- **部署**：`.env.example` 新增環境變數說明、Dockerfile / docker-compose 文件更新
