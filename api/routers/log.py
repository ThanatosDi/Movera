from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.models import database as db_models
from api.models import fastapi as fa_models
from api.models.database import get_session
from api.repositories.log import LogRepository
from api.utils.logger import logger

router = APIRouter(
    prefix="/log",
    tags=["Log"],
)


@router.get(
    "/task/{task_id}",
    summary="取得任務日誌",
    description="根據任務 ID，檢索與該任務關聯的所有日誌條目。",
    response_model=list[fa_models.Log],
    responses={
        500: {"model": fa_models.HTTPError, "description": "Internal server error"},
    },
)
def get_task_logs(task_id: str, session: Session = Depends(get_session)):
    """
    取得任務日誌。

    - **session**: 資料庫 session 依賴。
    """
    try:
        return LogRepository().get_task_log(session, task_id)
    except Exception as e:
        logger.error(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.post(
    "",
    summary="建立新日誌",
    description="根據提供的資料建立一個新的日誌條目。日誌條目包含任務 ID、操作類型、描述和時間戳。",
    response_model=fa_models.Log,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"model": fa_models.HTTPError, "description": "Task not found"},
        500: {"model": fa_models.HTTPError, "description": "Internal server error"},
    },
)
def create_log(log: fa_models.LogCreate, session: Session = Depends(get_session)):
    """
    建立一個新的日誌條目。

    - **log**: 包含日誌詳細資訊的請求主體。
    - **session**: 資料庫 session 依賴。
    """
    db_log = db_models.Log(**log.model_dump())
    try:
        created_log = LogRepository().create(session, db_log)
        return created_log
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found. The specified task_id does not exist.",
        )
    except Exception as e:
        session.rollback()
        logger.error(f"建立 log 發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred.",
        )


@router.delete(
    "",
    summary="刪除日誌",
    description="根據日誌 ID 或日期刪除日誌。提供 log_id 以刪除單個日誌，或提供 before_date 以刪除該日期之前的所有日誌。",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": fa_models.HTTPError, "description": "Bad Request"},
        404: {"model": fa_models.HTTPError, "description": "Log not found"},
        500: {"model": fa_models.HTTPError, "description": "Internal server error"},
    },
)
def delete_log(
    log_id: Optional[int] = Query(None, description="要刪除的日誌 ID"),
    before_date: Optional[date] = Query(
        None, description="刪除此日期之前建立的日誌 (YYYY-MM-DD)"
    ),
    session: Session = Depends(get_session),
):
    """
    刪除日誌條目。

    - **log_id**: 要刪除的特定日誌的 ID。
    - **before_date**: 刪除此日期之前的所有日誌。
    - **session**: 資料庫 session 依賴。
    """
    if (log_id is None and before_date is None) or (
        log_id is not None and before_date is not None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="請提供 'log_id' 或 'before_date' 其中一個參數，但不能同時提供。",
        )

    try:
        repo = LogRepository()
        if log_id is not None:
            deleted_count = repo.delete_log_by_id(session, log_id)
            if deleted_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"找不到 ID 為 {log_id} 的日誌。",
                )
            return {"message": f"成功刪除 ID 為 {log_id} 的日誌。"}

        if before_date is not None:
            deleted_count = repo.delete_logs_before_date(session, before_date)
            return {
                "message": f"成功刪除 {before_date} 之前的 {deleted_count} 筆日誌。"
            }
    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        logger.error(f"刪除日誌時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="刪除日誌時發生意外錯誤。",
        )


@router.get(
    "/{task_id}",
    summary="取得任務日誌",
    description="根據任務 ID，檢索與該任務關聯的所有日誌條目。",
    response_model=list[fa_models.Log],
    deprecated=True,
)
def get_log_by_task_id(task_id: str, session: Session = Depends(get_session)):
    """
    取得任務日誌。

    - **session**: 資料庫 session 依賴。
    """
    return LogRepository().get_by_task_id(session, task_id)
