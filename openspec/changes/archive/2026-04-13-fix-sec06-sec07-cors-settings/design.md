## Context

SEC-06 和 SEC-07 都是設定層面的安全問題，修復範圍小且互不依賴，合併在一個 change 中處理。

## Goals / Non-Goals

**Goals:**
- CORS 僅允許實際使用的 HTTP 方法和標頭
- settings API 僅接受已知的設定 key，過濾未知 key

**Non-Goals:**
- 不修改 CORS origins（目前已限制 localhost，合理）
- 不新增 API 端點

## Decisions

### 1. CORS methods/headers 明確列舉

**選擇：** `allow_methods=["GET", "POST", "PUT", "DELETE"]`，`allow_headers=["Content-Type", "Authorization"]`。

**理由：** 專案只使用這些 HTTP 方法。`Authorization` 預留給未來身份驗證。

### 2. Settings key 白名單使用靜態集合

**選擇：** 在 `setting.py` router 中定義 `_ALLOWED_SETTING_KEYS` 集合，在 `update_settings()` 中過濾。

**理由：** 在 router 層攔截最明確，且避免修改 SettingService 的通用邏輯。未知 key 靜默忽略（不回傳錯誤），因為前端不會送出未知 key，此行為僅防禦惡意請求。

### 3. 白名單 key 清單

根據現有 schemas 和前端使用情況：`timezone`、`locale`、`allowed_directories`、`allowed_source_directories`。

## Risks / Trade-offs

- **[風險] 未來新增設定時忘記加入白名單** → 在白名單定義處加上註解提醒
- **[取捨] 靜默忽略 vs 回傳錯誤** → 選擇靜默忽略，避免合法前端因多送欄位而報錯
