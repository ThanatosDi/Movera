# api/routers/task.py
from typing import List

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from core import schemas
from core.database import get_db
from core.repositories.task import TaskRepository
from core.services.task import TaskService

router = APIRouter(prefix="/api/v1", tags=["Tasks"])


def get_task_service(db: Session = Depends(get_db)) -> TaskService:
    """
    取得一個TaskService的實例

    Args:
        db (Session, optional): SQLAlchemy的Session物件. Defaults to Depends(get_db).

    Returns:
        TaskService: TaskService的實例
    """
    repo = TaskRepository(db)
    return TaskService(repo)


@router.get(
    "/tasks",
    response_model=List[schemas.Task],
    summary="獲取所有任務",
    response_description="所有任務的列表",
)
def get_all_tasks(service: TaskService = Depends(get_task_service)):
    """
    獲取資料庫中所有任務的完整列表。

    這個 API 用於查詢系統中存在的所有任務，並返回一個包含任務物件的陣列。

    回應內容:
    - `id`: 任務的唯一識別碼
    - `name`: 任務的名稱
    - `include`: 任務的檔案名稱關鍵字
    - `move_to`: 任務的移動到位置
    - `src_filename`: 檔案規則
    - `dst_filename`: 重新命名規則
    - `rename_rule`: 任務的重新命名規則 (regex | parse | None)
    - `enabled`: 任務是否啟用
    - `created_at`: 任務的建立時間
    """
    return service.get_all_tasks()


@router.get(
    "/task/{task_id}",
    response_model=schemas.Task,
    summary="獲取單一任務",
    response_description="所有單一任務的資料",
)
def get_one_task(task_id: str, service: TaskService = Depends(get_task_service)):
    """
    獲取資料庫中指定任務的資料。

    這個 API 用於查詢系統中存在的所有任務，並返回一個任務物件。

    回應內容:
    - `id`: 任務的唯一識別碼
    - `name`: 任務的名稱
    - `include`: 任務的檔案名稱關鍵字
    - `move_to`: 任務的移動到位置
    - `src_filename`: 檔案規則
    - `dst_filename`: 重新命名規則
    - `rename_rule`: 任務的重新命名規則 (regex | parse | None)
    - `enabled`: 任務是否啟用
    - `created_at`: 任務的建立時間
    """
    return service.get_one_task(task_id)


@router.post(
    "/task",
    response_model=schemas.Task,
    status_code=status.HTTP_201_CREATED,
    summary="創建一個新任務",
    response_description="成功創建的任務資訊",
)
def create_task(
    task: schemas.TaskCreate, service: TaskService = Depends(get_task_service)
):
    """
    根據提供的資料創建一個新的任務。

    API 會驗證傳入的資料，並在資料庫中建立一個新的任務紀錄。

    回應內容:
    - `id`: 任務的唯一識別碼
    - `name`: 任務的名稱
    - `include`: 任務的檔案名稱關鍵字
    - `move_to`: 任務的移動到位置
    - `src_filename`: 檔案規則
    - `dst_filename`: 重新命名規則
    - `rename_rule`: 任務的重新命名規則 (regex | parse | None)
    - `enabled`: 任務是否啟用
    - `created_at`: 任務的建立時間
    """
    return service.create_task(task)


@router.put(
    "/task/{task_id}",
    response_model=schemas.Task,
    summary="更新指定任務",
    response_description="成功更新後的任務資訊",
)
def update_task(
    task_id: str,
    task_update: schemas.TaskUpdate,
    service: TaskService = Depends(get_task_service),
):
    """
    根據任務 ID 更新現有的任務。

    這個 API 允許使用者修改任務的特定欄位，例如狀態或參數。

    回應內容:
    - `id`: 任務的唯一識別碼
    - `name`: 任務的名稱
    - `include`: 任務的檔案名稱關鍵字
    - `move_to`: 任務的移動到位置
    - `src_filename`: 檔案規則
    - `dst_filename`: 重新命名規則
    - `rename_rule`: 任務的重新命名規則 (regex | parse | None)
    - `enabled`: 任務是否啟用
    - `created_at`: 任務的建立時間
    """
    return service.update_task(task_id, task_update)


@router.delete(
    "/task/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="刪除指定任務",
    response_description="任務成功刪除，沒有回應內容",
)
def delete_task(task_id: str, service: TaskService = Depends(get_task_service)):
    """
    根據任務 ID 刪除一個現有的任務。

    這個操作是永久性的，成功後不會返回任何內容 (HTTP 204)。

    回應內容:
    - `None`: 這個請求成功時不會返回任何內容。
    """
    service.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/tasks/stats",
    response_model=schemas.TaskStats,
    summary="Get Task Statistics",
    response_description="An object containing task statistics.",
)
def get_task_stats(service: TaskService = Depends(get_task_service)):
    """
    檢索關於任務狀態的統計數據。


    回應內容:
    - `enabled`: 任務啟用的數量。
    - `disabled`: 任務停用的數量。
    """
    return service.get_task_stats()
