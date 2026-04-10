from fastapi import APIRouter, Depends

from backend import schemas
from backend.dependencies import depends_tag_service
from backend.services.tag_service import TagService

router = APIRouter(prefix="/api/v1", tags=["Tags"])


@router.get("/tags", response_model=list[schemas.Tag_], summary="獲取所有標籤")
def get_all_tags(service: TagService = Depends(depends_tag_service)):
    return service.get_all_tags()


@router.post("/tags", response_model=schemas.Tag_, status_code=201, summary="建立標籤")
def create_tag(tag: schemas.TagCreate, service: TagService = Depends(depends_tag_service)):
    return service.create_tag(tag)


@router.put("/tags/{tag_id}", response_model=schemas.Tag_, summary="更新標籤")
def update_tag(tag_id: str, tag: schemas.TagUpdate, service: TagService = Depends(depends_tag_service)):
    return service.update_tag(tag_id, tag)


@router.delete("/tags/{tag_id}", status_code=204, summary="刪除標籤")
def delete_tag(tag_id: str, service: TagService = Depends(depends_tag_service)):
    service.delete_tag(tag_id)
