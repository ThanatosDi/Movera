from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.repositories.log import LogRepository
from backend.repositories.preset_rule import PresetRuleRepository
from backend.repositories.setting import SettingRepository
from backend.repositories.tag import TagRepository
from backend.repositories.task import TaskRepository
from backend.services.log_service import LogService
from backend.services.directory_service import DirectoryService
from backend.services.preset_rule_service import PresetRuleService
from backend.services.preview_service import ParsePreviewService, RegexPreviewService
from backend.services.setting_service import SettingService
from backend.services.tag_service import TagService
from backend.services.task_service import TaskService


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


def depends_allowed_directories(
    setting_service: SettingService = Depends(depends_setting_service),
) -> list[str]:
    """Dependency to get the allowed directories from settings."""
    return setting_service.get_allowed_directories()
