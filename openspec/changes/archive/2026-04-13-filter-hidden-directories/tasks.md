## 1. 前置準備

- [x] 1.1 確認現有測試全部通過

## 2. 後端 — 擴展目錄過濾

### 2.1 🔴 紅燈 — 撰寫測試

- [x] 2.1.1 撰寫測試：`_is_hidden_directory()` 對 `.`、`#`、`@` 開頭回傳 True
- [x] 2.1.2 撰寫測試：`_is_hidden_directory()` 對正常目錄名稱回傳 False
- [x] 2.1.3 執行測試，確認失敗

### 2.2 🟢 綠燈 — 實作

- [x] 2.2.1 新增 `_is_hidden_directory(name)` 靜態方法
- [x] 2.2.2 替換 `_scan_directories()` 中的 `startswith(".")` 為 `_is_hidden_directory()`
- [x] 2.2.3 替換 `_has_subdirectories()` 中的 `startswith(".")` 為 `_is_hidden_directory()`
- [x] 2.2.4 執行全部測試確認通過

## 3. 整合測試

- [x] 3.1 執行全部後端測試
- [x] 3.2 執行 `uv run ruff check backend/services/directory_service.py`
