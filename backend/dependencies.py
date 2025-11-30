from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.repositories.setting import SettingRepository
from backend.repositories.task import TaskRepository
from backend.services.settingService import SettingService
from backend.services.taskService import TaskService


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
