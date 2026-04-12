import re

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from backend import schemas
from backend.dependencies import depends_parse_preview_service, depends_regex_preview_service
from backend.services.preview_service import ParsePreviewService, RegexPreviewService

router = APIRouter(prefix="/api/v1", tags=["Preview"])


@router.post(
    "/preview/parse",
    summary="Parse 預覽",
)
def preview_parse(
    payload: schemas.ParsePreviewRequest,
    service: ParsePreviewService = Depends(depends_parse_preview_service),
):
    return service.preview(
        src_pattern=payload.src_pattern,
        text=payload.text,
        dst_pattern=payload.dst_pattern,
    )


@router.post(
    "/preview/regex",
    summary="Regex 預覽",
)
def preview_regex(
    payload: schemas.RegexPreviewRequest,
    service: RegexPreviewService = Depends(depends_regex_preview_service),
):
    try:
        return service.preview(
            src_pattern=payload.src_pattern,
            text=payload.text,
            dst_pattern=payload.dst_pattern,
        )
    except (TimeoutError, re.error) as e:
        return JSONResponse(
            status_code=422,
            content={"detail": f"Regex 執行超時或錯誤: {str(e)}"},
        )
