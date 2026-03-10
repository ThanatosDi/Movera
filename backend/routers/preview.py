from fastapi import APIRouter

from backend import schemas
from backend.services.previewService import ParsePreviewService, RegexPreviewService

router = APIRouter(prefix="/api/v1", tags=["Preview"])


@router.post(
    "/preview/parse",
    summary="Parse 預覽",
)
def preview_parse(payload: schemas.ParsePreviewRequest):
    service = ParsePreviewService()
    return service.preview(
        src_pattern=payload.src_pattern,
        text=payload.text,
        dst_pattern=payload.dst_pattern,
    )


@router.post(
    "/preview/regex",
    summary="Regex 預覽",
)
def preview_regex(payload: schemas.RegexPreviewRequest):
    service = RegexPreviewService()
    return service.preview(
        src_pattern=payload.src_pattern,
        text=payload.text,
        dst_pattern=payload.dst_pattern,
    )
