from fastapi import APIRouter

from core.schemas.parse_preview import ParsePreviewRequest, ParsePreviewResponse
from core.services.parse_preview import ParsePreviewService

# 路由器實例，設定前綴和標籤
router = APIRouter(prefix="/api/v1", tags=["ParsePreview"])


@router.post(
    "/parse-preview",
    response_model=ParsePreviewResponse,
    summary="解析樣式和文字，回傳解析結果和格式化後的預覽",
    response_description="包含解析結果和格式化後的預覽。",
)
def handle_parse_preview(request: ParsePreviewRequest) -> ParsePreviewResponse:
    """
    接收解析樣式和文字，回傳解析結果和格式化後的預覽。
    """
    # 呼叫服務層的 preview 方法
    preview_result = ParsePreviewService.preview(
        src_pattern=request.src_pattern,
        text=request.text,
        dst_pattern=request.dst_pattern,
    )
    return preview_result
