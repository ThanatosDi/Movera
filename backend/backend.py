import asyncio
import os
import sys

if __name__ == "__main__" and "." not in sys.path:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.exceptions.directory_exception import (
    DirectoryAccessDenied,
    DirectoryNotFound,
)
from backend.exceptions.tag_exception import (
    InvalidTagColor,
    TagAlreadyExists,
    TagNotFound,
)
from backend.exceptions.task_exception import TaskAlreadyExists, TaskNotFound
from backend.middlewares import setup_cors, setup_gzip
from backend.routers import directory, log, preview, setting, tag, task, webhook
from backend.utils.logger import logger


def _run_alembic_upgrade():
    """同步執行 Alembic 遷移"""
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


async def run_migrations():
    try:
        logger.info("開始資料庫遷移...")
        await asyncio.to_thread(_run_alembic_upgrade)
        logger.info("資料庫遷移完成")
    except Exception as e:
        logger.info(f"遷移失敗: {e}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load
    await run_migrations()
    yield
    # Clean up
    pass


app = FastAPI(
    lifespan=lifespan,
    title="Movera API",
    description="API for managing file moving and renaming tasks.",
    version="4.0.0",
)


# Exception handlers
@app.exception_handler(TaskNotFound)
async def task_not_found_handler(request: Request, exc: TaskNotFound):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(TaskAlreadyExists)
async def task_already_exists_handler(request: Request, exc: TaskAlreadyExists):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(TagNotFound)
async def tag_not_found_handler(request: Request, exc: TagNotFound):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(TagAlreadyExists)
async def tag_already_exists_handler(request: Request, exc: TagAlreadyExists):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(InvalidTagColor)
async def invalid_tag_color_handler(request: Request, exc: InvalidTagColor):
    return JSONResponse(status_code=422, content={"detail": str(exc)})


@app.exception_handler(DirectoryNotFound)
async def directory_not_found_handler(request: Request, exc: DirectoryNotFound):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(DirectoryAccessDenied)
async def directory_access_denied_handler(
    request: Request, exc: DirectoryAccessDenied
):
    return JSONResponse(status_code=403, content={"detail": str(exc)})


# Middlewares
setup_cors(app)
setup_gzip(app)


app.include_router(task.router)
app.include_router(tag.router)
app.include_router(setting.router)
app.include_router(log.router)
app.include_router(preview.router)
app.include_router(webhook.router)
app.include_router(directory.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")