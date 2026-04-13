## 1. 前置準備

- [x] 1.1 確認現有測試全部通過

## 2. 後端 — safe_format 工具函式

### 2.1 🔴 紅燈 — 撰寫測試

- [x] 2.1.1 撰寫測試：正常 `{key}` 替換回傳正確結果
- [x] 2.1.2 撰寫測試：`{key.attr}` 語法不被替換（保留原始佔位符）
- [x] 2.1.3 撰寫測試：`{key[0]}` 語法不被替換
- [x] 2.1.4 撰寫測試：未匹配的 key 保留原始佔位符
- [x] 2.1.5 執行測試，確認失敗

### 2.2 🟢 綠燈 — 實作

- [x] 2.2.1 在 `backend/utils/safe_format.py` 實作 `safe_format(template, mapping)` 函式
- [x] 2.2.2 執行測試確認通過

## 3. 後端 — 替換呼叫端

- [x] 3.1 替換 `backend/utils/rename.py:34` 的 `self.dst.format(**template.named)` 為 `safe_format(self.dst, template.named)`
- [x] 3.2 替換 `backend/services/preview_service.py:49` 的 `format_str.format(**groups)` 為 `safe_format(format_str, groups)`
- [x] 3.3 執行全部後端測試確認通過

## 4. 整合測試

- [x] 4.1 執行全部後端測試
- [x] 4.2 執行 `uv run ruff check backend/utils/safe_format.py backend/utils/rename.py backend/services/preview_service.py`
