from typing import Generator

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.repositories.log import LogRepository
from backend.repositories.preset_rule import PresetRuleRepository
from backend.repositories.setting import SettingRepository
from backend.repositories.tag import TagRepository
from backend.repositories.task import TaskRepository
from backend.repositories.user import UserRepository
from backend.repositories.webhook_token import WebhookTokenRepository
from backend.services.auth_service import AuthService
from backend.services.log_service import LogService
from backend.services.directory_service import DirectoryService
from backend.services.preset_rule_service import PresetRuleService
from backend.services.preview_service import ParsePreviewService, RegexPreviewService
from backend.services.secret_service import SecretService
from backend.services.setting_service import SettingService
from backend.services.tag_service import TagService
from backend.services.task_service import TaskService
from backend.services.webhook_token_service import WebhookTokenService
from backend.utils.jwt import InvalidToken, decode_access_token


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency to get a database session.
    Ensures the session is closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def depends_task_repository(
    db: Session = Depends(get_db),
) -> TaskRepository:
    """Dependency to get a TaskRepository instance."""
    return TaskRepository(db=db)


def depends_task_service(
    repository: TaskRepository = Depends(depends_task_repository),
) -> TaskService:
    """Dependency to get a TaskService instance."""
    return TaskService(repository=repository)


def depends_setting_repository(
    db: Session = Depends(get_db),
) -> SettingRepository:
    """Dependency to get a SettingRepository instance."""
    return SettingRepository(db=db)


def depends_setting_service(
    repository: SettingRepository = Depends(depends_setting_repository),
) -> SettingService:
    """Dependency to get a SettingService instance."""
    return SettingService(repository=repository)


def depends_directory_service(
    setting_service: SettingService = Depends(depends_setting_service),
) -> DirectoryService:
    """Dependency to get a DirectoryService instance."""
    return DirectoryService(setting_service=setting_service)


def depends_parse_preview_service() -> ParsePreviewService:
    """Dependency to get a ParsePreviewService instance."""
    return ParsePreviewService()


def depends_regex_preview_service() -> RegexPreviewService:
    """Dependency to get a RegexPreviewService instance."""
    return RegexPreviewService()


def depends_preset_rule_repository(
    db: Session = Depends(get_db),
) -> PresetRuleRepository:
    """Dependency to get a PresetRuleRepository instance."""
    return PresetRuleRepository(db=db)


def depends_preset_rule_service(
    repository: PresetRuleRepository = Depends(depends_preset_rule_repository),
) -> PresetRuleService:
    """Dependency to get a PresetRuleService instance."""
    return PresetRuleService(repository=repository)


def depends_tag_repository(
    db: Session = Depends(get_db),
) -> TagRepository:
    """Dependency to get a TagRepository instance."""
    return TagRepository(db=db)


def depends_tag_service(
    repository: TagRepository = Depends(depends_tag_repository),
) -> TagService:
    """Dependency to get a TagService instance."""
    return TagService(repository=repository)


def depends_log_repository(
    db: Session = Depends(get_db),
) -> LogRepository:
    """Dependency to get a LogRepository instance."""
    return LogRepository(db=db)


def depends_log_service(
    repository: LogRepository = Depends(depends_log_repository),
) -> LogService:
    """Dependency to get a LogService instance."""
    return LogService(repository=repository)


# --- Auth / Secret ---


def depends_secret_service(
    repository: SettingRepository = Depends(depends_setting_repository),
) -> SecretService:
    """Dependency to get a SecretService instance."""
    return SecretService(repository=repository)


def get_secret(request: Request) -> str:
    """取得啟動時解析並快取於 app.state 的 JWT secret。"""
    return request.app.state.secret_key


def depends_user_repository(
    db: Session = Depends(get_db),
) -> UserRepository:
    """Dependency to get a UserRepository instance."""
    return UserRepository(db=db)


def depends_auth_service(
    repository: UserRepository = Depends(depends_user_repository),
    secret: str = Depends(get_secret),
) -> AuthService:
    """Dependency to get an AuthService instance."""
    return AuthService(repository=repository, secret=secret)


def depends_webhook_token_repository(
    db: Session = Depends(get_db),
) -> WebhookTokenRepository:
    """Dependency to get a WebhookTokenRepository instance."""
    return WebhookTokenRepository(db=db)


def depends_webhook_token_service(
    repository: WebhookTokenRepository = Depends(depends_webhook_token_repository),
) -> WebhookTokenService:
    """Dependency to get a WebhookTokenService instance."""
    return WebhookTokenService(repository=repository)


def _extract_bearer(authorization: str | None) -> str | None:
    """從 Authorization 標頭取出 Bearer token 值。"""
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1].strip()


def require_jwt(
    secret: str = Depends(get_secret),
    authorization: str | None = Header(default=None),
) -> str:
    """保護 /api/v1/* 路由：要求合法且未過期的 JWT，回傳使用者識別。"""
    token = _extract_bearer(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="缺少有效的存取憑證")
    try:
        payload = decode_access_token(secret, token)
    except InvalidToken:
        raise HTTPException(status_code=401, detail="存取憑證無效或已過期")
    subject = payload.get("sub")
    if not subject:
        raise HTTPException(status_code=401, detail="存取憑證無效")
    return subject


def require_webhook_token(
    authorization: str | None = Header(default=None),
    service: WebhookTokenService = Depends(depends_webhook_token_service),
) -> None:
    """相容式保護 /webhook/*：無有效 token 時放行，存在有效 token 時要求合法 Bearer。"""
    if not service.is_enforced():
        return
    token = _extract_bearer(authorization)
    if not token or not service.verify(token):
        raise HTTPException(status_code=401, detail="缺少或無效的 webhook token")
