"""
測試設定和共用 fixtures
"""

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from backend.database import Base
from backend.models.log import Log
from backend.models.setting import Setting
from backend.models.task import Task
from backend.repositories.log import LogRepository
from backend.repositories.setting import SettingRepository
from backend.repositories.task import TaskRepository
from backend.services.logService import LogService
from backend.services.settingService import SettingService
from backend.services.taskService import TaskService


@pytest.fixture(scope="function")
def db_engine():
    """建立測試用的 in-memory SQLite 資料庫引擎"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    # 啟用外鍵約束
    @event.listens_for(Engine, "connect")
    def _fk_pragma_on_connect(dbapi_con, con_record):
        dbapi_con.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine) -> Session:
    """建立測試用的資料庫 session"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine,
    )
    session = TestingSessionLocal()
    yield session
    session.close()


# --- Repository Fixtures ---


@pytest.fixture
def task_repository(db_session) -> TaskRepository:
    """建立 TaskRepository 實例"""
    return TaskRepository(db=db_session)


@pytest.fixture
def setting_repository(db_session) -> SettingRepository:
    """建立 SettingRepository 實例"""
    return SettingRepository(db=db_session)


@pytest.fixture
def log_repository(db_session) -> LogRepository:
    """建立 LogRepository 實例"""
    return LogRepository(db=db_session)


# --- Service Fixtures ---


@pytest.fixture
def task_service(task_repository) -> TaskService:
    """建立 TaskService 實例"""
    return TaskService(repository=task_repository)


@pytest.fixture
def setting_service(setting_repository) -> SettingService:
    """建立 SettingService 實例"""
    return SettingService(repository=setting_repository)


@pytest.fixture
def log_service(log_repository) -> LogService:
    """建立 LogService 實例"""
    return LogService(repository=log_repository)


# --- Sample Data Fixtures ---


@pytest.fixture
def sample_task_data() -> dict:
    """範例任務資料"""
    return {
        "name": "測試任務",
        "include": "測試關鍵字",
        "move_to": "/downloads/test",
        "src_filename": r"(.+) - (\d+).mp4",
        "dst_filename": r"\1 - S01E\2.mp4",
        "rename_rule": "regex",
        "enabled": True,
    }


@pytest.fixture
def sample_task_data_2() -> dict:
    """第二個範例任務資料"""
    return {
        "name": "第二個任務",
        "include": "另一個關鍵字",
        "move_to": "/downloads/anime",
        "src_filename": "{title} - {episode}.mp4",
        "dst_filename": "{title} - S01E{episode}.mp4",
        "rename_rule": "parse",
        "enabled": False,
    }


@pytest.fixture
def sample_log_data() -> dict:
    """範例日誌資料 (需要搭配 task_id)"""
    return {
        "level": "INFO",
        "message": "測試日誌訊息",
    }


@pytest.fixture
def sample_setting_data() -> dict:
    """範例設定資料"""
    return {
        "key": "timezone",
        "value": "Asia/Taipei",
    }


# --- Helper Functions ---


@pytest.fixture
def create_settings(db_session):
    """建立預設設定的輔助函數"""

    def _create_settings(settings_list: list[dict]):
        for setting_data in settings_list:
            setting = Setting(**setting_data)
            db_session.add(setting)
        db_session.commit()

    return _create_settings
