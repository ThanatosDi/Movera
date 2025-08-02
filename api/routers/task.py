from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from api.models.database import Task, get_session
from api.models.fastapi import HTTPError, TaskCreate, TaskStatus, TaskUpdate
from api.models.fastapi import Task as TaskObject
from api.repositories.task import TaskRepository
from api.utils.logger import logger

router = APIRouter(
    prefix="/task",
    tags=["Task"],
)


@router.get(
    "s",
    summary="取得所有任務",
    description="從資料庫中檢索所有已設定的任務列表。",
    response_model=List[TaskObject],
)
def get_tasks(session: Session = Depends(get_session)):
    return TaskRepository().get_all(session)

@router.get(
    "s/status",
    summary="取得所有任務狀態",
    description="從資料庫中檢索所有已設定的任務列表。",
    response_model=TaskStatus,
    responses={
        500: {"model": HTTPError, "description": "Internal server error"},
    },
)
def task_status(session: Session = Depends(get_session)):
    try:
        return TaskRepository().all_status(session)
    except Exception as e:
        logger.error(e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )


@router.post(
    "",
    summary="建立新任務",
    description="根據提供的資料建立一個新的任務。任務名稱 (`name`) 必須是唯一的。",
    response_model=TaskObject,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": HTTPError, "description": "任務名稱已存在或輸入資料無效"},
    },
)
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    _task = Task(
        name=task.name,
        include=task.include,
        move_to=task.move_to,
        src_filename_regex=task.src_filename_regex,
        dst_filename_regex=task.dst_filename_regex,
    )
    try:
        TaskRepository().create(session, _task)
        session.refresh(_task)
        return _task
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task with name '{task.name}' already exists.",
        )


@router.get(
    "/{task_id}",
    summary="取得單一任務",
    description="使用任務的唯一識別碼 (UUID) 來檢索特定的任務詳細資訊。",
    response_model=TaskObject,
    responses={
        404: {"model": HTTPError, "description": "找不到具有指定 ID 的任務"},
    },
)
def get_task(task_id: str, session: Session = Depends(get_session)):
    task = TaskRepository().get(session, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' not found.",
        )
    return task


@router.put(
    "/{task_id}",
    summary="更新任務",
    description="使用任務 ID 找到對應的任務，並用請求中提供的資料更新其內容。",
    response_model=TaskObject,
    responses={
        404: {"model": HTTPError, "description": "找不到具有指定 ID 的任務"},
        400: {"model": HTTPError, "description": "任務名稱已存在或輸入資料無效"},
    },
)
def update_task(
    task_id: str, task: TaskUpdate, session: Session = Depends(get_session)
):
    _task = Task(
        name=task.name,
        include=task.include,
        move_to=task.move_to,
        src_filename_regex=task.src_filename_regex,
        dst_filename_regex=task.dst_filename_regex,
    )
    try:
        repo = TaskRepository()
        repo.update(session, task_id, _task)
        return repo.get(session, task_id)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task name '{task.name}' may already exist.",
        )


@router.delete(
    "/{task_id}",
    summary="刪除任務",
    description="永久刪除指定的任務。此操作無法復原。",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": HTTPError, "description": "找不到具有指定 ID 的任務"},
    },
)
def delete_task(task_id: str, session: Session = Depends(get_session)):
    try:
        TaskRepository().delete(session, task_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' not found.",
        )
    return