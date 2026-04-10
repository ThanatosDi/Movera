from fastapi import APIRouter, Depends

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
    return service.preview(
        src_pattern=payload.src_pattern,
        text=payload.text,
        dst_pattern=payload.dst_pattern,
    )
