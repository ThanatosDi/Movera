import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.modules.task_processor import process_completed_download
from core.schemas.webhook import QBittorrentPayload

# It's better to use the project's configured logger if available.
# For now, we'll use the standard logging module.
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/webhook",
    tags=["Webhook"],
)


@router.post(
    "/qbittorrent/on-complete",
    summary="QBittorrent Download Completion Webhook",
    response_description="Confirmation message that the webhook was received.",
)
async def qbittorrent_on_complete(
    payload: QBittorrentPayload, background_tasks: BackgroundTasks
):
    """
    Receives a webhook from qBittorrent when a download is complete.

    This endpoint will immediately return a success message and schedule
    the actual processing to run in the background.
    """
    try:
        logger.info(f"Webhook received for content path: {payload.file_path}")

        # Schedule the heavy lifting to be done in the background
        background_tasks.add_task(process_completed_download, payload.file_path)

        return {
            "status": "success",
            "message": "Webhook received and processing scheduled in the background.",
            "content_path": payload.file_path,
        }
    except Exception as e:
        logger.error(f"💥 Error processing qBittorrent webhook: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Internal Server Error while processing webhook."
        )


# It's better to use the project's configured logger if available.
# For now, we'll use the standard logging module.
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/webhook",
    tags=["Webhook"],
)


@router.post(
    "/qbittorrent/on-complete",
    summary="QBittorrent Download Completion Webhook",
    response_description="Confirmation message that the webhook was received.",
)
async def qbittorrent_on_complete(payload: QBittorrentPayload):
    """
    Receives a webhook from qBittorrent when a download is complete.

    You can add your custom logic here to process the downloaded file/folder.
    For example, moving the file, triggering a library scan, etc.
    """
    try:
        # For now, we just log the received path for demonstration.
        # This will be visible in the console where you run the FastAPI server.
        print(f"✅ Download complete. Content path: {payload.content_path}")
        logger.info(f"Download complete. Content path: {payload.content_path}")

        # You can add your custom logic here.
        # For example:
        # process_download(payload.content_path)

        return {
            "status": "success",
            "message": "Webhook received successfully.",
            "content_path": payload.content_path,
        }
    except Exception as e:
        logger.error(f"💥 Error processing qBittorrent webhook: {e}", exc_info=True)
        # Print the error for immediate visibility during development
        print(f"💥 Error processing qBittorrent webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error while processing webhook.")
