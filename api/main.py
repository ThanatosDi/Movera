import os
import sys

if __name__ == "__main__" and "." not in sys.path:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import FastAPI

from api.middlewares import setup_cors
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
    version="1.0.0",
)

# Setup CORS
setup_cors(app)

# Include routers
app.include_router(task.router)
app.include_router(log.router)
app.include_router(webhook.router)
app.include_router(setting.router)


@app.get("/", tags=["Root"], status_code=200)
def read_root():
    return {"message": "Welcome to Movera API"}


@app.get("/health", tags=["Health"], status_code=200)
def health():
    return {"status": "OK"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
