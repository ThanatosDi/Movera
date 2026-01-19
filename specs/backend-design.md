# Python 後端設計規範

## 1. 專案結構

```
backend/
├── main.py              # FastAPI 應用程式入口點
├── models/              # SQLAlchemy ORM 模型
│   ├── __init__.py
│   ├── task.py          # Task 模型
│   ├── log.py           # Log 模型
│   └── setting.py       # Setting 模型
├── schemas/             # Pydantic 資料驗證模式
│   ├── __init__.py
│   ├── task.py          # TaskCreate, TaskUpdate, Task
│   ├── log.py           # Log schema
│   └── setting.py       # Settings schema
├── repositories/        # 資料存取層
│   ├── __init__.py
│   ├── taskRepository.py
│   ├── logRepository.py
│   └── settingRepository.py
├── services/            # 商業邏輯層
│   ├── __init__.py
│   ├── taskService.py
│   ├── logService.py
│   ├── settingService.py
│   └── wsService.py     # WebSocket 事件處理
├── routers/             # HTTP API 路由
│   ├── __init__.py
│   ├── taskRouter.py
│   ├── logRouter.py
│   └── settingRouter.py
├── exceptions/          # 自定義例外
│   ├── __init__.py
│   ├── taskException.py
│   ├── wsException.py
│   └── workerException.py
├── enums/               # 列舉定義
│   └── wsEventEnum.py
├── worker/              # 背景任務處理
│   └── worker.py
└── database/            # 資料庫配置
    └── database.py
```

## 2. 架構模式

### 2.1 分層架構
採用三層架構模式，各層職責分明：

```
┌─────────────────────────────────────┐
│  Router / WebSocket Handler         │  ← API 入口層
├─────────────────────────────────────┤
│  Service Layer                      │  ← 商業邏輯層
├─────────────────────────────────────┤
│  Repository Layer                   │  ← 資料存取層
├─────────────────────────────────────┤
│  SQLAlchemy ORM / Database          │  ← 資料層
└─────────────────────────────────────┘
```

### 2.2 依賴注入
使用服務容器模式管理依賴：

```python
@dataclass
class Services:
    """服務容器，集中管理所有服務實例"""
    task: TaskService
    log: LogService
    setting: SettingService
```

### 2.3 事件處理器註冊模式
WebSocket 事件使用裝飾器註冊：

```python
def register_event_handler(event: wsEventEnum):
    """裝飾器：註冊 WebSocket 事件處理器"""
    def decorator(func):
        _event_handlers[event] = func.__name__
        return func
    return decorator

# 使用範例
@register_event_handler(wsEventEnum.GET_TASKS)
async def _handle_get_tasks(self, payload: Any) -> list[dict]:
    return [task.model_dump() for task in self.services.task.get_tasks()]
```

## 3. 命名規範

### 3.1 檔案命名
- **模型**: `camelCase.py` (例: `task.py`, `setting.py`)
- **服務**: `camelCaseService.py` (例: `taskService.py`)
- **倉儲**: `camelCaseRepository.py` (例: `taskRepository.py`)
- **路由**: `camelCaseRouter.py` (例: `taskRouter.py`)
- **例外**: `camelCaseException.py` (例: `taskException.py`)

### 3.2 類別命名
- **模型類別**: `PascalCase` (例: `Task`, `Log`, `Setting`)
- **Schema 類別**: `PascalCase` 帶後綴 (例: `TaskCreate`, `TaskUpdate`)
- **服務類別**: `PascalCaseService` (例: `TaskService`)
- **倉儲類別**: `PascalCaseRepository` (例: `TaskRepository`)
- **例外類別**: `PascalCase` (例: `TaskNotFound`, `TaskAlreadyExists`)

### 3.3 方法命名
- **CRUD 操作**: `get_*`, `create_*`, `update_*`, `delete_*`
- **批量操作**: `get_all_*`, `delete_all_*`
- **私有方法**: `_method_name` (單底線前綴)
- **WebSocket 處理器**: `_handle_event_name`

### 3.4 變數命名
- **一般變數**: `snake_case`
- **常數**: `UPPER_SNAKE_CASE`
- **私有變數**: `_variable_name`

## 4. 類型提示規範

### 4.1 函式簽名
所有函式必須包含完整類型提示：

```python
def get_task_by_id(self, task_id: str) -> models.Task | None:
    """根據 ID 取得任務"""
    return self.repository.get_by_id(task_id)

def create_task(self, task_data: schemas.TaskCreate) -> models.Task:
    """建立新任務"""
    return self.repository.create(task_data)
```

### 4.2 泛型使用
使用 TypeVar 定義泛型：

```python
from typing import TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

def _validate_payload(self, schema_class: type[T], payload: dict) -> T:
    return schema_class(**payload)
```

### 4.3 Optional 處理
使用 `| None` 語法而非 `Optional`：

```python
# 推薦
def find_task(task_id: str) -> Task | None:
    ...

# 避免
def find_task(task_id: str) -> Optional[Task]:
    ...
```

## 5. 錯誤處理規範

### 5.1 自定義例外層級

```python
# 基礎例外
class MoveraException(Exception):
    """所有 Movera 例外的基礎類別"""
    pass

# 領域例外
class TaskNotFound(MoveraException):
    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task not found: {task_id}")

class TaskAlreadyExists(MoveraException):
    def __init__(self, task_name: str):
        self.task_name = task_name
        super().__init__(f"Task already exists: {task_name}")

# Worker 例外
class RenameOperationError(MoveraException):
    def __init__(self, filepath: str, reason: str):
        super().__init__(f"Rename failed for {filepath}: {reason}")

class MoveOperationError(MoveraException):
    def __init__(self, filepath: str, reason: str):
        super().__init__(f"Move failed for {filepath}: {reason}")
```

### 5.2 服務層驗證模式

```python
def _get_task_or_raise(self, task_id: str) -> models.Task:
    """取得任務，若不存在則拋出 TaskNotFound"""
    task = self.get_task_by_id(task_id)
    if task is None:
        raise TaskNotFound(task_id)
    return task

def update_task(self, task_id: str, task_data: schemas.TaskUpdate) -> models.Task:
    task = self._get_task_or_raise(task_id)
    return self.repository.update(task, task_data)
```

### 5.3 WebSocket 錯誤回應格式

```python
{
    "event": "error",
    "payload": {
        "error": "TaskNotFound",      # 錯誤類型 (用於前端識別)
        "message": "Task not found: abc123"  # 人類可讀訊息
    },
    "timestamp": 1705123456789,
    "requestId": "req-123",
    "success": False
}
```

## 6. 測試規範

### 6.1 測試檔案結構

```
tests/
└── backend/
    ├── conftest.py           # 共用 fixtures
    ├── test_task_service.py  # 服務層測試
    ├── test_ws_service.py    # WebSocket 測試
    ├── test_worker.py        # Worker 測試
    └── test_repositories.py  # 倉儲層測試
```

### 6.2 測試命名規範
- 測試檔案: `test_<module>.py`
- 測試類別: `Test<ClassName>`
- 測試方法: `test_<method>_<scenario>_<expected_result>`

```python
class TestTaskService:
    def test_create_task_with_valid_data_returns_task(self):
        ...

    def test_create_task_with_duplicate_name_raises_exception(self):
        ...
```

### 6.3 Fixture 使用

```python
@pytest.fixture
def mock_task_repository():
    return MagicMock(spec=TaskRepository)

@pytest.fixture
def task_service(mock_task_repository):
    return TaskService(mock_task_repository)
```

## 7. API 設計規範

### 7.1 RESTful HTTP 端點

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/api/v1/tasks` | 取得所有任務 |
| GET | `/api/v1/tasks/{task_id}` | 取得單一任務 |
| POST | `/api/v1/tasks` | 建立任務 |
| PUT | `/api/v1/tasks/{task_id}` | 更新任務 |
| DELETE | `/api/v1/tasks/{task_id}` | 刪除任務 |
| GET | `/api/v1/settings` | 取得設定 |

### 7.2 WebSocket 事件命名
使用 `snake_case` 命名：

```python
class wsEventEnum(str, Enum):
    GET_TASKS = "get_tasks"
    CREATE_TASK = "create_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    GET_SETTINGS = "get_settings"
    UPDATE_SETTING = "update_setting"
```

---

*文件版本: 1.0*
*最後更新: 2026-01-19*
