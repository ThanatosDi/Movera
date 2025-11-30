import os
import sys

if __name__ == "__main__" and "." not in sys.path:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import FastAPI

from backend.middlewares import setup_cors, setup_gzip
from backend.routers import setting, websocket
from backend.utils.logger import logger


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
    version="3.0.0",
)


# Middlewares
setup_cors(app)
setup_gzip(app)


app.include_router(websocket.router)
app.include_router(setting.router)


@app.get("/")
async def root():
    return {"message": "Hello, World!"}
