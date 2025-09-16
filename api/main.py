import os
import sys

if __name__ == "__main__" and "." not in sys.path:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.middlewares import setup_cors, setup_gzip
from api.routers import log, setting, task, webhook
from core.utils.logger import logger as _logger

logger = _logger.bind(app="api")


async def run_migrations():
    try:
        logger.info("開始資料庫遷移...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
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
    version="2.0.0",
)

# Middlewares
setup_cors(app)
setup_gzip(app)

# Include routers
app.include_router(task.router)
app.include_router(log.router)
app.include_router(webhook.router)
app.include_router(setting.router)


@app.get("/api/v1/health", tags=["Health"], status_code=200)
def health():
    return {"status": "OK"}


# === 前端靜態檔案 ===
app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")


# catch-all，非 /api 與 /webhook 的路徑，一律回傳 index.html
@app.get("/{full_path:path}")
async def serve_vue(full_path: str):
    if full_path.startswith("api/") or full_path.startswith("webhook/"):
        # 這裡丟 404 給 FastAPI 原生處理
        return {"detail": "Not Found"}
    if full_path.endswith((".ico", ".svg", ".png", ".jpg", ".jpeg", ".webmanifest")):
        return FileResponse(os.path.join("dist", full_path))
    index_path = os.path.join("dist", "index.html")
    return FileResponse(index_path)
