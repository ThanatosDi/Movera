# api/routers/log.py
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core import schemas
from core.database import get_db
from core.repositories.log import LogRepository
from core.services.log import LogService

router = APIRouter(prefix="/api/v1", tags=["Logs"])


def get_log_service(db: Session = Depends(get_db)) -> LogService:
    """
    依賴函數：取得 LogService 的實例

    依賴 db 來建立 LogRepository，然後將其交由 LogService 的建構函數來產生實例

    Args:
        db (Session, optional): SQLAlchemy 的 Session 物件. Defaults to Depends(get_db).

    Returns:
        LogService: LogService 的實例
    """
    repo = LogRepository(db)
    return LogService(repo)


@router.get(
    "/log/{task_id}",
    response_model=List[schemas.Log],
    summary="Get Logs for a Specific Task",
    response_description="A list of logs associated with the task.",
)
def get_logs_for_task(task_id: str, service: LogService = Depends(get_log_service)):
    """
    根據提供的任務 ID 檢索所有相關的日誌紀錄。

    這個 API 端點允許客戶端查詢特定任務的執行歷史和詳細輸出。

    回應內容:
    - A JSON array of log objects, where each object contains:
      - `id`: The unique identifier for the log entry.
      - `task_id`: The ID of the task this log belongs to.
      - `level`: The log level (e.g., INFO, ERROR).
      - `message`: The log message.
      - `created_at`: The timestamp when the log was created.
    """
    return service.get_logs_for_task(task_id)


@router.post(
    "/log",
    response_model=schemas.Log,
    status_code=status.HTTP_201_CREATED,
    summary="創建一個新的日誌項目",
    response_description="成功創建的日誌項目",
    # include_in_schema=False,
)
def create_log(log: schemas.LogCreate, service: LogService = Depends(get_log_service)):
    """
    在資料庫中創建一個新的日誌紀錄。

    這個 API 通常由內部服務呼叫，用來記錄特定任務的執行情況。

    回應內容:
    - `id`: 新日誌的唯一識別碼
    - `task_id`: 關聯任務的 ID
    - `level`: 日誌等級 (例如: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    - `message`: 日誌訊息內容
    - `created_at`: 日誌的建立時間
    """
    print(log)
    return service.create_log(log)
