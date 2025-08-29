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
    - `status`: 任務目前的狀態 (e.g., "pending", "completed")
    - `params`: 任務的參數
    - `created_at`: 任務的建立時間
    - `updated_at`: 任務的最後更新時間
    """
    return service.get_all_tasks()


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
    - `id`: 新任務的唯一識別碼
    - `name`: 任務的名稱
    - `status`: 任務的初始狀態 (通常是 "pending")
    - `params`: 任務的參數
    - `created_at`: 任務的建立時間
    - `updated_at`: 任務的最後更新時間
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
    - `id`: 被更新任務的唯一識別碼
    - `name`: 任務的名稱
    - `status`: 更新後的任務狀態
    - `params`: 更新後的任務參數
    - `created_at`: 任務的建立時間
    - `updated_at`: 任務的最後更新時間
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

    這包括各種狀態（如待處理、進行中、已完成）的任務數量。

    回應內容:
    - `total`: The total number of tasks.
    - `pending`: The number of tasks with 'pending' status.
    - `in_progress`: The number of tasks with 'in_progress' status.
    - `completed`: The number of tasks with 'completed' status.
    - `failed`: The number of tasks with 'failed' status.
    """
    return service.get_task_stats()
