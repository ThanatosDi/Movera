import asyncio
import os
import sys

if __name__ == "__main__" and "." not in sys.path:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from backend.dependencies import require_jwt, require_webhook_token

from backend.exceptions.directory_exception import (
    DirectoryAccessDenied,
    DirectoryNotFound,
)
from backend.exceptions.preset_rule_exception import (
    PresetRuleAlreadyExists,
    PresetRuleNotFound,
)
from backend.exceptions.tag_exception import (
    InvalidTagColor,
    TagAlreadyExists,
    TagNotFound,
)
from backend.exceptions.task_exception import TaskAlreadyExists, TaskNotFound
from backend.middlewares import setup_cors, setup_gzip
from backend.routers import (
    auth,
    directory,
    log,
    preset_rule,
    preview,
    setting,
    tag,
    task,
    webhook,
    webhook_token,
)
from backend.utils.logger import logger

from . import __version__


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


def _initialize_auth(app: FastAPI):
    """解析 JWT secret 並（必要時）依環境變數建立管理員帳號。

    必須在資料庫遷移完成後執行，因為 secret 與帳號皆需讀寫資料表。
    """
    from backend.database import SessionLocal
    from backend.repositories.setting import SettingRepository
    from backend.repositories.user import UserRepository
    from backend.services.auth_service import AuthService
    from backend.services.secret_service import SecretService
    from backend.utils.env_config import (
        get_env_admin_password,
        get_env_admin_username,
    )

    db = SessionLocal()
    try:
        secret = SecretService(SettingRepository(db)).resolve_secret()
        app.state.secret_key = secret

        admin_username = get_env_admin_username()
        admin_password = get_env_admin_password()
        if admin_username and admin_password:
            AuthService(UserRepository(db), secret).seed_admin_from_env(
                admin_username, admin_password
            )
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load
    await run_migrations()
    _initialize_auth(app)
    yield
    # Clean up
    pass


app = FastAPI(
    lifespan=lifespan,
    title="Movera API",
    description="API for managing file moving and renaming tasks.",
    version=__version__,
    docs_url="/api/docs" if os.getenv("ENV") == "development" else None,
    redoc_url="/api/redoc" if os.getenv("ENV") == "development" else None,
    openapi_url="/api/openapi.json" if os.getenv("ENV") == "development" else None,
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
async def directory_access_denied_handler(request: Request, exc: DirectoryAccessDenied):
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(PresetRuleNotFound)
async def preset_rule_not_found_handler(request: Request, exc: PresetRuleNotFound):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(PresetRuleAlreadyExists)
async def preset_rule_already_exists_handler(
    request: Request, exc: PresetRuleAlreadyExists
):
    return JSONResponse(status_code=409, content={"detail": str(exc)})


# Middlewares
setup_cors(app)
setup_gzip(app)


# 公開端點（不需 JWT）：登入、初始化、認證狀態
app.include_router(auth.router)

# 受保護的 /api/v1/* 端點：要求合法 JWT
_protected = [Depends(require_jwt)]
app.include_router(task.router, dependencies=_protected)
app.include_router(tag.router, dependencies=_protected)
app.include_router(preset_rule.router, dependencies=_protected)
app.include_router(setting.router, dependencies=_protected)
app.include_router(log.router, dependencies=_protected)
app.include_router(preview.router, dependencies=_protected)
app.include_router(directory.router, dependencies=_protected)
app.include_router(webhook_token.router, dependencies=_protected)

# Webhook 端點：相容式 token 驗證（無有效 token 放行，有則強制）
app.include_router(webhook.router, dependencies=[Depends(require_webhook_token)])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
