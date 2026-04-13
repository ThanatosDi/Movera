## Context

SEC-08 和 SEC-11 都是簡單的防禦性修改，互不依賴，合併處理。

## Goals / Non-Goals

**Goals:**
- 目錄掃描跳過 symlink
- 所有使用者輸入的 str 欄位有合理的 max_length

**Non-Goals:**
- 不修改前端

## Decisions

### 1. Symlink 檢查加在 `_is_hidden_directory()` 同層

**選擇：** 在 `_scan_directories()` 和 `_has_subdirectories()` 的迭代中加入 `entry.is_symlink()` 檢查。

**理由：** 與既有的隱藏目錄過濾邏輯在同一層級，簡潔明瞭。

### 2. max_length 依欄位用途決定

| 欄位類型 | max_length | 理由 |
|---------|-----------|------|
| 名稱類（name） | 255 | 一般命名不超過 255 字元 |
| 路徑類（move_to, filepath） | 4096 | Linux PATH_MAX |
| 規則類（include, pattern, src/dst_filename） | 1000 | 正則表達式和 parse 模式的合理上限 |
| 訊息類（message） | 5000 | 日誌訊息 |
| 顏色類（color） | 20 | 預定義色名 |
| 分類/標籤（category, tags） | 255 | 一般分類 |
