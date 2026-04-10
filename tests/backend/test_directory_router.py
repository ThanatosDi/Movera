"""
Directory Router 單元測試
"""

import json
import os
import tempfile

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base
from backend.dependencies import depends_directory_service
from backend.exceptions.directory_exception import (
    DirectoryAccessDenied,
    DirectoryNotFound,
)
from backend.models.setting import Setting
from backend.repositories.setting import SettingRepository
from backend.routers import directory
from backend.services.directory_service import DirectoryService
from backend.services.setting_service import SettingService


def create_test_app():
    """建立不含 lifespan 的測試用 FastAPI app"""
    test_app = FastAPI()
    test_app.include_router(directory.router)

    @test_app.exception_handler(DirectoryNotFound)
    async def handle_not_found(request: Request, exc: DirectoryNotFound):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @test_app.exception_handler(DirectoryAccessDenied)
    async def handle_access_denied(request: Request, exc: DirectoryAccessDenied):
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    return test_app


@pytest.fixture
def temp_dir_structure():
    """建立暫時目錄結構用於測試"""
    with tempfile.TemporaryDirectory() as root:
        os.makedirs(os.path.join(root, "anime", "show1"))
        os.makedirs(os.path.join(root, "movies"))
        yield root


@pytest.fixture
def client(temp_dir_structure):
    """建立 TestClient，使用獨立的 DB 和 service 鏈"""
    # 建立獨立的 in-memory DB
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()

    # 設定允許目錄
    setting = Setting(
        key="allowed_directories",
        value=json.dumps([temp_dir_structure]),
    )
    session.add(setting)
    session.commit()

    # 建立 service 鏈
    setting_repo = SettingRepository(db=session)
    setting_service = SettingService(repository=setting_repo)
    path_service = DirectoryService(setting_service=setting_service)

    test_app = create_test_app()

    def override_path_service():
        return path_service

    test_app.dependency_overrides[depends_directory_service] = override_path_service

    yield TestClient(test_app)

    session.close()
    Base.metadata.drop_all(bind=engine)


class TestDirectoryRouter:
    """測試 Directory Router"""

    def test_list_root_directories(self, client, temp_dir_structure):
        """測試 GET /api/v1/directories 無參數時回傳根目錄列表"""
        response = client.get("/api/v1/directories")
        assert response.status_code == 200
        data = response.json()
        assert "directories" in data
        assert len(data["directories"]) >= 1

    def test_list_subdirectories(self, client, temp_dir_structure):
        """測試 GET /api/v1/directories?path=... 回傳子目錄列表"""
        response = client.get(
            "/api/v1/directories", params={"path": temp_dir_structure}
        )
        assert response.status_code == 200
        data = response.json()
        names = [d["name"] for d in data["directories"]]
        assert "anime" in names
        assert "movies" in names

    def test_list_directories_access_denied(self, client):
        """測試查詢未允許目錄回傳 403"""
        response = client.get(
            "/api/v1/directories", params={"path": "/etc/secret"}
        )
        assert response.status_code == 403

    def test_list_directories_not_found(self, client, temp_dir_structure):
        """測試查詢不存在目錄回傳 404"""
        response = client.get(
            "/api/v1/directories",
            params={"path": os.path.join(temp_dir_structure, "nonexistent")},
        )
        assert response.status_code == 404
