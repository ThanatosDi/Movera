from fastapi import APIRouter, Body, Depends, HTTPException

from backend import schemas
from backend.dependencies import depends_task_service
from backend.schemas import TASK_BATCH_MAX_ITEMS
from backend.services.task_service import TaskService

router = APIRouter(prefix="/api/v1", tags=["Tasks"])


@router.get(
    "/tasks",
    response_model=list[schemas.Task],
    summary="獲取所有任務",
)
def get_all_tasks(service: TaskService = Depends(depends_task_service)):
    return service.get_all_tasks()


# --- Batch endpoints (placed before `/tasks/{task_id}` to avoid path conflict) ---


@router.post(
    "/tasks/batch",
    response_model=schemas.TaskBatchResult,
    status_code=201,
    summary="批量建立任務",
)
def batch_create_tasks(
    payload: schemas.TaskBatchCreate,
    service: TaskService = Depends(depends_task_service),
):
    if len(payload.items) == 0:
        raise HTTPException(status_code=400, detail="items must not be empty")
    if len(payload.items) > TASK_BATCH_MAX_ITEMS:
        raise HTTPException(
            status_code=400,
            detail=f"items exceeds maximum of {TASK_BATCH_MAX_ITEMS}",
        )
    created = service.batch_create_tasks(payload.items)
    return schemas.TaskBatchResult(
        items=[schemas.Task.model_validate(t) for t in created]
    )


@router.put(
    "/tasks/batch",
    response_model=schemas.TaskBatchResult,
    summary="批量更新任務",
)
def batch_update_tasks(
    payload: schemas.TaskBatchUpdate,
    service: TaskService = Depends(depends_task_service),
):
    if len(payload.items) == 0:
        raise HTTPException(status_code=400, detail="items must not be empty")
    if len(payload.items) > TASK_BATCH_MAX_ITEMS:
        raise HTTPException(
            status_code=400,
            detail=f"items exceeds maximum of {TASK_BATCH_MAX_ITEMS}",
        )
    updated = service.batch_update_tasks(payload.items)
    return schemas.TaskBatchResult(
        items=[schemas.Task.model_validate(t) for t in updated]
    )


@router.delete(
    "/tasks/batch",
    response_model=schemas.TaskBatchResult,
    summary="批量刪除任務",
)
def batch_delete_tasks(
    payload: schemas.TaskBatchDelete = Body(...),
    service: TaskService = Depends(depends_task_service),
):
    if len(payload.ids) == 0:
        raise HTTPException(status_code=400, detail="ids must not be empty")
    if len(payload.ids) > TASK_BATCH_MAX_ITEMS:
        raise HTTPException(
            status_code=400,
            detail=f"ids exceeds maximum of {TASK_BATCH_MAX_ITEMS}",
        )
    deleted_ids = service.batch_delete_tasks(payload.ids)
    return schemas.TaskBatchResult(deleted_ids=deleted_ids)


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
