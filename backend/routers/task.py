from fastapi import APIRouter, Depends

from backend import schemas
from backend.dependencies import depends_task_service
from backend.services.task_service import TaskService

router = APIRouter(prefix="/api/v1", tags=["Tasks"])


@router.get(
    "/tasks",
    response_model=list[schemas.Task],
    summary="獲取所有任務",
)
def get_all_tasks(service: TaskService = Depends(depends_task_service)):
    return service.get_all_tasks()


@router.get(
    "/tasks/{task_id}",
    response_model=schemas.Task,
    summary="獲取指定任務",
)
def get_task(task_id: str, service: TaskService = Depends(depends_task_service)):
    return service._get_task_or_raise(task_id)


@router.post(
    "/tasks",
    response_model=schemas.Task,
    status_code=201,
    summary="建立任務",
)
def create_task(
    task: schemas.TaskCreate,
    service: TaskService = Depends(depends_task_service),
):
    return service.create_task(task)


@router.put(
    "/tasks/{task_id}",
    response_model=schemas.Task,
    summary="更新任務",
)
def update_task(
    task_id: str,
    task: schemas.TaskUpdate,
    service: TaskService = Depends(depends_task_service),
):
    return service.update_task(task_id, task)


@router.delete(
    "/tasks/{task_id}",
    status_code=204,
    summary="刪除任務",
)
def delete_task(task_id: str, service: TaskService = Depends(depends_task_service)):
    service.delete_task(task_id)
