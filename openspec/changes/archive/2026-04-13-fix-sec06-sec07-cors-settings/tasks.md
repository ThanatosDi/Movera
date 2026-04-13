## 1. 前置準備

- [x] 1.1 確認現有測試全部通過

## 2. SEC-06 — CORS 修復

### 2.1 🟢 綠燈 — 實作 CORS 限制

- [x] 2.1.1 修改 `backend/middlewares/cors.py`：`allow_methods` 改為 `["GET", "POST", "PUT", "DELETE"]`
- [x] 2.1.2 修改 `backend/middlewares/cors.py`：`allow_headers` 改為 `["Content-Type", "Authorization"]`
- [x] 2.1.3 執行全部後端測試確認通過

## 3. SEC-07 — Settings key 白名單

### 3.1 🔴 紅燈 — 撰寫測試

- [x] 3.1.1 撰寫測試：`PUT /api/v1/settings` 包含未知 key 時該 key 被忽略
- [x] 3.1.2 撰寫測試：合法 key 正常更新
- [x] 3.1.3 執行測試，確認失敗

### 3.2 🟢 綠燈 — 實作白名單過濾

- [x] 3.2.1 在 `setting.py` router 定義 `_ALLOWED_SETTING_KEYS` 集合
- [x] 3.2.2 在 `update_settings()` 中過濾掉不在白名單內的 key
- [x] 3.2.3 執行測試，確認通過

## 4. 整合測試

- [x] 4.1 執行全部後端測試 `uv run pytest tests/`
- [x] 4.2 執行全部前端測試 `npx vitest run`
- [x] 4.3 啟動伺服器，驗證前端設定頁面正常保存
- [x] 4.4 執行 `uv run ruff check backend/middlewares/cors.py backend/routers/setting.py`
