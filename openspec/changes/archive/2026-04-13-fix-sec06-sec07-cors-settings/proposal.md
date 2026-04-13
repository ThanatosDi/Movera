## Why

SEC-06：CORS middleware 使用 `allow_methods=["*"]` 和 `allow_headers=["*"]`，搭配 `allow_credentials=True` 擴大了攻擊面，不符合最小權限原則。

SEC-07：`PUT /api/v1/settings` 接受任意 `dict`，沒有 key 白名單驗證。攻擊者可注入任意設定 key 至資料庫，或在 `ALLOW_WEBUI_SETTING=true` 時修改安全關鍵設定。

## What Changes

- **SEC-06**：將 CORS `allow_methods` 限制為 `["GET", "POST", "PUT", "DELETE"]`，`allow_headers` 限制為 `["Content-Type", "Authorization"]`
- **SEC-07**：定義允許修改的設定 key 白名單，`update_settings()` 中過濾掉不在白名單內的 key

## Capabilities

### New Capabilities

### Modified Capabilities

## Impact

- **後端**：`backend/middlewares/cors.py`（CORS 設定）、`backend/routers/setting.py`（key 白名單過濾）
- **前端**：無修改（前端只使用白名單內的 key）
- **API**：`PUT /api/v1/settings` 會忽略不在白名單內的 key（靜默忽略，不回傳錯誤）
