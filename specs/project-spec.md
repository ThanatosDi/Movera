# 專案功能規格

## 1. 專案概述

**Movera** 是一個自動化檔案管理系統，專為 BT 下載器（如 qBittorrent）設計，當下載完成時自動移動和重新命名檔案。

### 核心功能
- 監控 BT 下載完成事件（透過 Webhook）
- 根據規則自動移動檔案到指定目錄
- 支援兩種重新命名模式：Regex 和 Parse
- 任務管理（CRUD、批量操作）
- 執行日誌記錄
- 多語系支援（zh-TW、en）

## 2. 資料模型

### 2.1 Task（任務）

```typescript
interface Task {
  id: string              // UUID，唯一識別碼
  name: string            // 任務名稱（唯一）
  include: string         // 檔名包含字串（用於匹配）
  move_to: string         // 目標目錄路徑
  rename_rule: 'regex' | 'parse' | null  // 重新命名規則類型
  src_filename: string | null   // 來源檔名規則
  dst_filename: string | null   // 目標檔名規則
  enabled: boolean        // 是否啟用
  created_at: string      // 建立時間 (ISO 8601)
  logs?: Log[]            // 關聯的執行日誌
}
```

### 2.2 Log（執行日誌）

```typescript
interface Log {
  id: string              // UUID
  task_id: string         // 關聯的任務 ID
  original_filename: string  // 原始檔案名稱
  new_filename: string | null  // 新檔案名稱（如有重新命名）
  move_to: string         // 移動目標路徑
  message: string         // 執行訊息
  status: 'success' | 'failed'  // 執行狀態
  created_at: string      // 執行時間
}
```

### 2.3 Settings（設定）

```typescript
interface Settings {
  timezone: string        // 時區 (例: 'Asia/Taipei')
  locale: string          // 語系 (例: 'zh-TW', 'en')
}
```

## 3. API 規格

### 3.1 HTTP REST API

| 方法 | 端點 | 說明 | 請求體 | 回應 |
|------|------|------|--------|------|
| GET | `/api/v1/tasks` | 取得所有任務 | - | `Task[]` |
| GET | `/api/v1/tasks/{id}` | 取得單一任務 | - | `Task` |
| POST | `/api/v1/tasks` | 建立任務 | `TaskCreate` | `Task` |
| PUT | `/api/v1/tasks/{id}` | 更新任務 | `TaskUpdate` | `Task` |
| DELETE | `/api/v1/tasks/{id}` | 刪除任務 | - | `{ message }` |
| GET | `/api/v1/settings` | 取得設定 | - | `Settings` |
| POST | `/webhook/download-complete` | 下載完成回呼 | `{ name, path }` | - |

### 3.2 WebSocket 事件

#### 客戶端 → 伺服器

| 事件 | Payload | 說明 |
|------|---------|------|
| `get_tasks` | `{}` | 取得所有任務 |
| `get_task` | `{ task_id: string }` | 取得單一任務 |
| `create_task` | `TaskCreate` | 建立任務 |
| `update_task` | `{ task_id, ...TaskUpdate }` | 更新任務 |
| `delete_task` | `{ task_id: string }` | 刪除任務 |
| `get_settings` | `{}` | 取得設定 |
| `update_setting` | `Settings` | 更新設定 |
| `regex_preview` | `{ test, src, dst }` | Regex 預覽 |
| `parse_preview` | `{ test, src, dst }` | Parse 預覽 |

#### 伺服器 → 客戶端

```typescript
interface WebSocketResponse<T> {
  event: string           // 對應的事件名稱
  payload: T              // 回應資料
  timestamp: number       // Unix 時間戳
  requestId: string       // 請求 ID（用於匹配）
  success: boolean        // 是否成功
}

// 錯誤回應
interface WebSocketErrorResponse {
  event: string
  payload: {
    error: string         // 錯誤類型
    message: string       // 錯誤訊息
  }
  success: false
}
```

## 4. 重新命名規則

### 4.1 Regex 模式
使用正規表達式捕獲群組進行重新命名：

```
來源規則: (.+)_(\d{2})\.(.+)
測試檔名: Show_01.mp4
目標規則: Episode_\2.\3
結果: Episode_01.mp4
```

**支援功能**:
- 編號群組 (`\1`, `\2`, `\3`...)
- 命名群組 (`(?P<name>...)` 和 `\g<name>`)

### 4.2 Parse 模式
使用 Python `parse` 套件的模板語法：

```
來源規則: {show}_{episode:d}.{ext}
測試檔名: Show_01.mp4
目標規則: Episode_{episode:02d}.{ext}
結果: Episode_01.mp4
```

**支援的格式指定符**:
- `d` - 整數
- `f` - 浮點數
- `w` - 字母數字
- `s` - 字串（預設）
- `l` - 小寫
- `u` - 大寫
- `ti` - 時間戳

## 5. 工作流程

### 5.1 下載完成處理流程

```
┌─────────────────────────────────────────────────────────────┐
│ 1. qBittorrent 下載完成                                      │
│    ↓                                                        │
│ 2. 呼叫 Webhook: POST /webhook/download-complete            │
│    Body: { name: "Show_01.mp4", path: "/downloads" }        │
│    ↓                                                        │
│ 3. Worker 接收並處理                                         │
│    ├─ match_task(): 根據 include 匹配任務                    │
│    ├─ perform_rename_operation(): 執行重新命名（如有規則）    │
│    └─ perform_move_operation(): 移動檔案到目標目錄           │
│    ↓                                                        │
│ 4. 記錄執行日誌                                              │
│    ↓                                                        │
│ 5. 推送即時通知（透過 WebSocket）                            │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 任務匹配邏輯

```python
def match_task(tasks: list[Task], filepath: str) -> Task | None:
    """匹配第一個 include 字串存在於 filepath 的任務"""
    for task in tasks:
        if task.include in filepath:
            return task
    return None
```

## 6. 頁面功能

### 6.1 首頁 (HomeView)
- 顯示任務統計（已啟用/已停用數量）
- 快速入口連結

### 6.2 任務清單 (TasksListView)
- 顯示所有任務列表
- 搜尋過濾功能
- 批量選擇模式
  - 批量啟用/停用
  - 批量刪除
- 點擊進入任務詳情

### 6.3 建立任務 (CreateTaskView)
- 任務表單
  - 名稱（必填，唯一）
  - 檔名包含（必填）
  - 移動目標（必填）
  - 重新命名規則（可選）
- 即時預覽
  - Regex 預覽元件
  - Parse 預覽元件

### 6.4 任務詳情 (TaskDetailView)
- 顯示/編輯任務設定
- 啟用/停用切換
- 刪除任務（需確認）
- 顯示執行日誌歷史

### 6.5 設定頁面 (SettingView)
- 語系選擇
- 時區設定

## 7. 錯誤代碼

| 錯誤代碼 | 說明 | HTTP 狀態碼 |
|---------|------|-------------|
| `TaskNotFound` | 找不到指定任務 | 404 |
| `TaskAlreadyExists` | 任務名稱已存在 | 409 |
| `PayloadValidationError` | 請求資料驗證失敗 | 400 |
| `UnHandledWebSocketEvent` | 未知的 WebSocket 事件 | 400 |
| `RenameOperationError` | 重新命名操作失敗 | 500 |
| `MoveOperationError` | 移動操作失敗 | 500 |

## 8. 國際化

### 支援語系
- `zh-TW` - 繁體中文（預設）
- `en` - 英文

### 翻譯檔案結構

```json
{
  "common": { ... },
  "components": {
    "taskForm": { ... },
    "parsePreview": { ... },
    "regexPreview": { ... }
  },
  "views": {
    "createTaskView": { ... },
    "taskDetailView": { ... }
  },
  "errors": { ... },
  "exceptions": { ... },
  "notifications": { ... }
}
```

## 9. 技術棧

### 後端
- **語言**: Python 3.12+
- **框架**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **資料庫**: SQLite
- **驗證**: Pydantic v2
- **WebSocket**: FastAPI WebSocket
- **測試**: pytest, pytest-asyncio

### 前端
- **框架**: Vue 3 (Composition API)
- **狀態管理**: Pinia
- **路由**: Vue Router 4
- **UI**: shadcn-vue + Tailwind CSS
- **國際化**: vue-i18n
- **建構工具**: Vite
- **測試**: Vitest + happy-dom

---

*文件版本: 1.0*
*最後更新: 2026-01-19*
