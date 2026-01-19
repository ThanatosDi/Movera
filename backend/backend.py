import asyncio
import os
import sys

if __name__ == "__main__" and "." not in sys.path:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import FastAPI

from backend.middlewares import setup_cors, setup_gzip
from backend.routers import setting, webhook, websocket
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
    version="3.1.0",
)


# Middlewares
setup_cors(app)
setup_gzip(app)


app.include_router(setting.router)
app.include_router(webhook.router)
app.include_router(websocket.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")