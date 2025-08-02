import threading
from contextlib import asynccontextmanager

import uvicorn
from alembic import command
from alembic.config import Config
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from api.routers import log, tag, task, task_tag_mapping

# from main import main


def run_migrations():
    try:
        print("開始資料庫遷移...")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("資料庫遷移完成")
    except Exception as e:
        logger.info(f"遷移失敗: {e}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load
    # await run_migrations()
    run_migrations()
    yield
    # Clean up
    pass


app = FastAPI(lifespan=lifespan, debug=True, root_path="/api/v1")


app.include_router(task.router)
app.include_router(tag.router)
app.include_router(task_tag_mapping.router)
app.include_router(log.router)
# app.include_router(setting.router)

# 掛載 Vue build 出來的靜態檔
# app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthy")
def healthy():
    return JSONResponse({"status": "healthy"}, status_code=status.HTTP_200_OK)


if __name__ == "__main__":
    # watchdog = threading.Thread(target=main, daemon=True)
    # watchdog.start()
    uvicorn.run("API:app", host="0.0.0.0", port=8080, reload=True)
