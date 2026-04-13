## Context

`DirectoryService` 有兩處目錄過濾：`_scan_directories()` 和 `_has_subdirectories()`。兩處都使用 `entry.name.startswith(".")` 條件。

## Goals / Non-Goals

**Goals:**
- 過濾 `.`、`#`、`@` 開頭的資料夾
- 提取過濾條件為共用函式

**Non-Goals:**
- 不修改前端

## Decisions

### 1. 提取 `_is_hidden_directory()` 共用方法

**選擇：** 在 `DirectoryService` 中新增 `_is_hidden_directory(name)` 靜態方法，兩處過濾邏輯共用。

**理由：** 避免重複，未來新增過濾前綴時只需修改一處。

### 2. 過濾前綴使用 tuple + `startswith()`

**選擇：** `name.startswith((".", "#", "@"))`，利用 Python `str.startswith()` 支援 tuple 參數。

**理由：** 簡潔、高效，且易於擴展。
