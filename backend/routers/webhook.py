from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException

from backend import __version__
from backend.schemas import QBittorrentPayload
from backend.worker.worker import process_completed_download

router = APIRouter(
    prefix="/webhook",
    tags=["Webhook"],
)


@router.get(
    "/status",
    summary="API 狀態",
    description="檢查 API 的狀態，並列出可用的 Webhook 端點。",
)
def webhook_status():
    """回傳 API 的當前狀態，並提供可用的 Webhook 路由資訊。"""
    return {
        "status": "ok",
        "version": __version__,  # 建議從統一的設定檔或 __version__ 變數中讀取
        "timestamp": datetime.now(UTC).isoformat(),
        "available_webhooks": [
            {
                "path": "/webhook/qbittorrent/on-complete",
                "method": "POST",
                "summary": "QBittorrent Download Completion Webhook",
                "description": "接收 qBittorrent 下載完成的通知，並在背景觸發檔案處理任務。",
            }
        ],
    }


@router.post(
    "/qbittorrent/on-complete",
    summary="QBittorrent Download Completion Webhook",
    response_description="Confirmation message that the webhook was received.",
)
async def qbittorrent_on_complete(
    payload: QBittorrentPayload, background_tasks: BackgroundTasks
):
    """
    處理 qBittorrent 下載完成 webhook 的 API。

    在 qBittorrent 的 "執行外部程式" 功能中設定以下 URL，以便在下載完成時將事件傳遞給這個 API：
    `http://localhost:8000/webhook/qbittorrent/on-complete`

    事件處理器會在背景任務中執行，避免在 API 請求中 block 掉進一步的請求。

    回應內容:
    - `status`: always "success"
    - `message`: "Webhook received and processing scheduled in the background."
    - `content_path`: the content path of the downloaded torrent
    """
    try:
        background_tasks.add_task(process_completed_download, payload.filepath)
        return {
            "status": "ok",
            "code": 200,
            "filepath": payload.filepath,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Internal Server Error while processing webhook."
        )
