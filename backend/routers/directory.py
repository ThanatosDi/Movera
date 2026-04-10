from typing import Optional

from fastapi import APIRouter, Depends, Query

from backend import schemas
from backend.dependencies import depends_directory_service
from backend.services.directory_service import DirectoryService

router = APIRouter(prefix="/api/v1", tags=["Directories"])


@router.get(
    "/directories",
    response_model=schemas.DirectoryListResponse,
    summary="瀏覽伺服器目錄",
    response_description="指定路徑下的子目錄列表",
)
def list_directories(
    path: Optional[str] = Query(None, description="要瀏覽的目錄路徑，未提供時回傳允許的根目錄"),
    service: DirectoryService = Depends(depends_directory_service),
):
    """
    瀏覽伺服器上的目錄結構。

    僅回傳後端設定中允許的目錄範圍內的子目錄。
    """
    directories = service.list_directories(path)
    return schemas.DirectoryListResponse(directories=directories)
