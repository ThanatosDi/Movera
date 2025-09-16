from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from api.models.database import Tag, get_session
from api.models.fastapi import HTTPError, TagCreate, TagUpdate
from api.models.fastapi import Tag as TagObject
from api.repositories.tag import TagRepository

router = APIRouter(
    prefix="/tag",
    tags=["Tag"],
)


@router.get(
    "s",
    summary="取得所有標籤",
    description="從資料庫中檢索所有已建立的標籤。",
    response_model=List[TagObject],
)
def get_tags(session: Session = Depends(get_session)):
    return TagRepository().get_all(session)


@router.post(
    "",
    summary="建立新標籤",
    description="根據提供的名稱和顏色建立一個新的標籤。標籤名稱 (`name`) 必須是唯一的。",
    response_model=TagObject,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": HTTPError, "description": "標籤名稱已存在或輸入資料無效"},
    },
)
def create_tag(tag: TagCreate, session: Session = Depends(get_session)):
    _tag = Tag(
        name=tag.name,
        color=tag.color,
    )
    try:
        TagRepository().create(session, _tag)
        session.refresh(_tag)
        return _tag
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag with name '{tag.name}' already exists.",
        )


@router.get(
    "/{tag_id}",
    summary="取得單一標籤",
    description="使用標籤的唯一識別碼 (ID) 來檢索特定的標籤詳細資訊。",
    response_model=TagObject,
    responses={
        404: {"model": HTTPError, "description": "找不到具有指定 ID 的標籤"},
    },
)
def get_tag(tag_id: int, session: Session = Depends(get_session)):
    tag = TagRepository().get(session, tag_id)
    if tag is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id '{tag_id}' not found.",
        )
    return tag


@router.put(
    "/{tag_id}",
    summary="更新標籤",
    description="使用標籤 ID 找到對應的標籤，並用請求中提供的資料更新其內容。",
    response_model=TagObject,
    responses={
        404: {"model": HTTPError, "description": "找不到具有指定 ID 的標籤"},
        400: {"model": HTTPError, "description": "標籤名稱已存在或輸入資料無效"},
    },
)
def update_tag(tag_id: int, tag: TagUpdate, session: Session = Depends(get_session)):
    _tag = Tag(
        name=tag.name,
        color=tag.color,
    )
    try:
        repo = TagRepository()
        repo.update(session, tag_id, _tag)
        return repo.get(session, tag_id)
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag name '{tag.name}' may already exist.",
        )


@router.delete(
    "/{tag_id}",
    summary="刪除標籤",
    description="永久刪除指定的標籤。此操作無法復原。",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": HTTPError, "description": "找不到具有指定 ID 的標籤"},
    },
)
def delete_tag(tag_id: int, session: Session = Depends(get_session)):
    try:
        TagRepository().delete(session, tag_id)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id '{tag_id}' not found.",
        )
    return