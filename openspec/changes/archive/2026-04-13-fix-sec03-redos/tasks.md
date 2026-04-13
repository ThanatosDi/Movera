## 1. 前置準備

- [x] 1.1 確認現有測試全部通過（`uv run pytest tests/` 和 `npx vitest run`）

## 2. 後端 — 安全正則表達式工具模組

### 2.1 🔴 紅燈 — 撰寫測試

- [x] 2.1.1 撰寫測試：`safe_compile()` 正常 pattern 回傳 compiled pattern
- [x] 2.1.2 撰寫測試：`safe_compile()` 超過長度限制時拋出 `ValueError`
- [x] 2.1.3 撰寫測試：`safe_search()` 正常匹配回傳 Match 物件
- [x] 2.1.4 撰寫測試：`safe_search()` 逾時時拋出 `RegexTimeoutError`
- [x] 2.1.5 撰寫測試：`safe_sub()` 正常替換回傳結果字串
- [x] 2.1.6 撰寫測試：`safe_sub()` 逾時時拋出 `RegexTimeoutError`
- [x] 2.1.7 執行測試，確認全部失敗

### 2.2 🟢 綠燈 — 實作 safe_regex 模組

- [x] 2.2.1 建立 `backend/utils/safe_regex.py`
- [x] 2.2.2 實作 `RegexTimeoutError(ValueError)` 自訂例外
- [x] 2.2.3 實作 `safe_compile(pattern, max_length=500)` 函式
- [x] 2.2.4 實作 `safe_search(pattern, string, timeout=3)` 函式
- [x] 2.2.5 實作 `safe_sub(pattern, repl, string, timeout=3)` 函式
- [x] 2.2.6 執行測試，確認全部通過

### 2.3 🔵 重構

- [x] 2.3.1 執行測試，確認仍然通過

## 3. 後端 — 替換 rename.py 的 regex 呼叫

### 3.1 🔴 紅燈 — 撰寫測試

- [x] 3.1.1 撰寫測試：`RegexRenameRule.rename()` 使用惡意 pattern 時拋出例外而非掛起
- [x] 3.1.2 執行測試，確認失敗

### 3.2 🟢 綠燈 — 替換 rename.py

- [x] 3.2.1 將 `rename.py` 的 `re.compile()` / `re.sub()` 替換為 `safe_compile()` / `safe_sub()`
- [x] 3.2.2 執行全部 rename 相關測試確認通過

## 4. 後端 — 替換 preview_service.py 的 regex 呼叫

### 4.1 🔴 紅燈 — 撰寫測試

- [x] 4.1.1 撰寫測試：`RegexPreviewService._match()` 使用惡意 pattern 時拋出例外
- [x] 4.1.2 執行測試，確認失敗

### 4.2 🟢 綠燈 — 替換 preview_service.py

- [x] 4.2.1 將 `preview_service.py` 的 `re.compile()` / `re.search()` / `re.sub()` 替換為安全版本
- [x] 4.2.2 在 `RegexPreviewService.preview()` 中捕獲 `RegexTimeoutError`，回傳空結果與錯誤訊息
- [x] 4.2.3 執行全部 preview 相關測試確認通過

## 5. 後端 — Preview Router 錯誤處理

- [x] 5.1 確認 preview router 在 `ValueError` / `RegexTimeoutError` 時回傳 400 錯誤
- [x] 5.2 執行全部後端測試 `uv run pytest tests/ -v`

## 6. 整合測試

- [x] 6.1 執行全部前端測試 `npx vitest run`
- [x] 6.2 執行前端型別檢查 `npx vue-tsc --noEmit`
- [x] 6.3 執行 `uv run ruff check backend/utils/safe_regex.py backend/utils/rename.py backend/services/preview_service.py`
