from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.models.database import Task, get_session
from api.models.fastapi import HTTPError
from api.models.fastapi import Tag as TagResponse
from api.repositories.task_tag_mapping import TaskTagMappingRepository

router = APIRouter(
    prefix="/task/{task_id}/tag",
    tags=["Task-Tag Mapping"],
)


@router.get(
    "s",
    summary="取得任務的所有標籤",
    description="根據任務 ID，檢索與該任務關聯的所有標籤列表。",
    response_model=List[TagResponse],
    responses={
        404: {"model": HTTPError, "description": "找不到具有指定 ID 的任務"},
    },
)
def get_tags_for_task(task_id: str, session: Session = Depends(get_session)):
    # First, check if the task itself exists
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' not found.",
        )
    # The repository method handles returning the tags
    return TaskTagMappingRepository().get_tags_by_task(session, task_id)


@router.post(
    "/{tag_id}",
    summary="將標籤關聯至任務",
    description="建立一個任務和標籤之間的關聯。如果關聯已存在，此操作不會重複建立。",
    status_code=status.HTTP_201_CREATED,
    response_model=TagResponse,
    responses={
        404: {"model": HTTPError, "description": "找不到指定的任務或標籤"},
    },
)
def add_tag_to_task(task_id: str, tag_id: int, session: Session = Depends(get_session)):
    repo = TaskTagMappingRepository()
    result = repo.create(session, task_id, tag_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' or Tag with id '{tag_id}' not found.",
        )
    # To return the added tag, we can get it from the result
    added_tag = next((tag for tag in result.tags if tag.id == tag_id), None)
    return added_tag


@router.delete(
    "/{tag_id}",
    summary="從任務移除標籤關聯",
    description="移除一個任務和標籤之間的現有關聯。此操作不會刪除任務或標籤本身。",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": HTTPError, "description": "找不到指定的任務、標籤，或兩者之間沒有關聯"},
    },
)
def remove_tag_from_task(
    task_id: str, tag_id: int, session: Session = Depends(get_session)
):
    repo = TaskTagMappingRepository()
    result = repo.delete(session, task_id, tag_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id '{task_id}' or Tag with id '{tag_id}' not found.",
        )
    if result is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id '{tag_id}' is not associated with Task with id '{task_id}'.",
        )
    return