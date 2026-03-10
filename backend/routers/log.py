from fastapi import APIRouter, Depends

from backend import schemas
from backend.dependencies import depends_log_service
from backend.services.logService import LogService

router = APIRouter(prefix="/api/v1", tags=["Logs"])


@router.get(
    "/tasks/{task_id}/logs",
    response_model=list[schemas.Log],
    summary="獲取指定任務的日誌",
)
def get_logs_by_task_id(
    task_id: str, service: LogService = Depends(depends_log_service)
):
    return service.get_logs_by_task_id(task_id)
