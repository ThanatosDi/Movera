import logging
import os

import uvicorn
from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.main import app
from core.utils.logger import logger as _logger

logger = _logger.bind(app="web")


def main():
    # 在背景執行緒啟動檔案監控服務
    # monitoring_service_thread = threading.Thread(target=start_monitoring_service, daemon=True)
    # monitoring_service_thread.start()

    # 在主執行緒啟動 FastAPI 伺服器
    logger.info("Starting Movera API server...")

    # 將 Uvicorn / FastAPI 的標準 logging 導入 Loguru，並保留 stdlib extra
    class InterceptHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            from loguru import logger as __logger

            try:
                level = __logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            # 維持正確的呼叫堆疊深度（避免顯示為 logging 自身）
            frame, depth = logging.currentframe(), 2
            while frame and frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(
                depth=depth,
                exception=record.exc_info,
            ).log(level, record.getMessage())

    # root_logger = logging.getLogger()
    # root_logger.handlers = [InterceptHandler()]
    # root_logger.setLevel(logging.NOTSET)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        log = logging.getLogger(name)
        log.handlers = [InterceptHandler()]
        log.propagate = False

    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, log_config=None)


if __name__ == "__main__":
    main()
