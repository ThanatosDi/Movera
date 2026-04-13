## Context

目前有三處使用者控制的正則表達式：
1. `RegexRenameRule.rename()` — Worker 執行重新命名時
2. `RegexPreviewService._match()` — 前端即時預覽匹配結果
3. `RegexPreviewService._format()` — 前端即時預覽替換結果

三處都直接使用 `re.compile()` + `re.search()`/`re.sub()`，無任何保護。

## Goals / Non-Goals

**Goals:**
- 防止 ReDoS 攻擊，限制正則表達式長度與執行時間
- 維持現有功能邏輯完全不變（匹配、替換行為一致）
- 正則表達式無效或逾時時給使用者清楚的錯誤訊息

**Non-Goals:**
- 不使用第三方正則表達式引擎（如 `re2`），避免增加編譯依賴
- 不修改前端程式碼

## Decisions

### 1. 使用 `concurrent.futures.ThreadPoolExecutor` 實作逾時

**選擇：** 將正則表達式執行包裝在執行緒中，設定逾時上限（預設 3 秒）。

**理由：**
- Python 的 `re` 模組不支援原生逾時
- `signal.alarm` 在 Windows 上不可用，且在多執行緒環境中不安全
- `concurrent.futures` 是標準庫，跨平台，且可在 ASGI worker 中安全使用
- `re2` 需要 C++ 編譯依賴，增加 Docker 映像大小和建構複雜度

**替代方案：** 使用 `google-re2` — 被否決，因為需要安裝系統級 C++ 依賴。

### 2. 正則表達式長度限制：500 字元

**選擇：** 在編譯前檢查 pattern 長度，超過 500 字元直接拒絕。

**理由：** 一般的檔案名稱匹配規則不會超過 200 字元。500 字元提供充裕空間，同時阻擋異常長的惡意 pattern。

### 3. 集中在工具函式中處理，不修改呼叫端邏輯

**選擇：** 新增 `backend/utils/safe_regex.py`，提供 `safe_compile()`、`safe_search()`、`safe_sub()` 函式。呼叫端只需替換 import。

**理由：** 最小化修改範圍，降低引入 bug 的風險。呼叫端的邏輯流程完全不變。

**影響層級：** 新增工具模組 + 修改 Service / Utils 層的 import。

### 4. 逾時時拋出自訂例外

**選擇：** 新增 `RegexTimeoutError(ValueError)` 例外。Preview API 捕獲後回傳 400；Worker 捕獲後記錄錯誤日誌並跳過該任務。

**理由：** 繼承 `ValueError` 讓既有的錯誤處理程式碼（如 `rename.py` 的 `except ValueError`）可以自然捕獲。

## Risks / Trade-offs

- **[風險] 執行緒逾時增加少量效能開銷** → 正常情況下正則表達式在毫秒內完成，逾時機制只在異常情況觸發
- **[取捨] 3 秒逾時可能對極長文字的合法匹配過於嚴格** → 檔案名稱通常不超過 255 字元，3 秒綽綽有餘
