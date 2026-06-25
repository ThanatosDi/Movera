from fastapi import APIRouter, Depends, HTTPException

from backend import schemas
from backend.dependencies import depends_auth_service
from backend.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.get(
    "/status",
    response_model=schemas.AuthStatusResponse,
    summary="認證狀態",
    description="回報系統是否尚未建立任何管理員帳號（需初始化設定）。",
)
def auth_status(service: AuthService = Depends(depends_auth_service)):
    return schemas.AuthStatusResponse(needs_setup=service.needs_setup())


@router.post(
    "/setup",
    response_model=schemas.TokenResponse,
    summary="初始化管理員帳號",
    description="在尚無任何帳號時建立第一組管理員帳密，成功後直接回傳存取憑證。",
)
def setup(
    payload: schemas.SetupRequest,
    service: AuthService = Depends(depends_auth_service),
):
    if not service.needs_setup():
        raise HTTPException(status_code=409, detail="管理員帳號已存在，無法重複初始化")
    service.create_admin(payload.username, payload.password)
    access_token = service.issue_token(payload.username)
    return schemas.TokenResponse(access_token=access_token)


@router.post(
    "/login",
    response_model=schemas.TokenResponse,
    summary="管理員登入",
    description="以使用者名稱與前端 SHA-256 雜湊後的密碼登入，成功回傳 JWT。",
)
def login(
    payload: schemas.LoginRequest,
    service: AuthService = Depends(depends_auth_service),
):
    if not service.verify_credentials(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="使用者名稱或密碼錯誤")
    access_token = service.issue_token(payload.username)
    return schemas.TokenResponse(access_token=access_token)
