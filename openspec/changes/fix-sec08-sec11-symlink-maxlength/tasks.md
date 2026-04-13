## 1. 前置準備

- [x] 1.1 確認現有測試全部通過

## 2. SEC-08 — Symlink 過濾

### 2.1 🔴 紅燈 — 撰寫測試

- [x] 2.1.1 撰寫測試：`_scan_directories()` 跳過 symlink 目錄
- [x] 2.1.2 執行測試，確認失敗

### 2.2 🟢 綠燈 — 實作

- [x] 2.2.1 在 `_scan_directories()` 加入 `entry.is_symlink()` 檢查
- [x] 2.2.2 在 `_has_subdirectories()` 加入 `entry.is_symlink()` 檢查
- [x] 2.2.3 執行測試確認通過

## 3. SEC-11 — Pydantic max_length

### 3.1 🟢 綠燈 — 加入 max_length

- [x] 3.1.1 TaskBase：`name`(255)、`include`(1000)、`move_to`(4096)、`src_filename`(1000)、`dst_filename`(1000)
- [x] 3.1.2 TagBase：`name`(255)、`color`(20)
- [x] 3.1.3 PresetRuleBase：`name`(255)、`pattern`(1000)
- [x] 3.1.4 LogBase：`message`(5000)
- [x] 3.1.5 SettingBase / SettingUpdate：`key`(255)、`value`(5000)
- [x] 3.1.6 DownloaderOnCompletePayload：`filepath`(4096)、`category`(255)、`tags`(255)
- [x] 3.1.7 ParsePreviewRequest / RegexPreviewRequest：`src_pattern`(1000)、`text`(1000)、`dst_pattern`(1000)
- [x] 3.1.8 執行全部後端測試確認通過

## 4. 整合測試

- [x] 4.1 執行全部後端測試
- [x] 4.2 執行 `uv run ruff check backend/services/directory_service.py backend/schemas.py`
