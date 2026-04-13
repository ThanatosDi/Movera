"""
DirectoryService (目錄瀏覽) 單元測試
"""

import json
import os
import tempfile

import pytest

from backend.exceptions.directory_exception import (
    DirectoryAccessDenied,
    DirectoryNotFound,
)
from backend.models.setting import Setting
from backend.services.directory_service import DirectoryService
from backend.services.setting_service import SettingService


@pytest.fixture
def temp_dir_structure():
    """建立暫時目錄結構用於測試"""
    with tempfile.TemporaryDirectory() as root:
        # 建立子目錄結構
        os.makedirs(os.path.join(root, "anime", "show1"))
        os.makedirs(os.path.join(root, "anime", "show2"))
        os.makedirs(os.path.join(root, "movies"))
        os.makedirs(os.path.join(root, ".hidden"))
        os.makedirs(os.path.join(root, "#recycle"))
        os.makedirs(os.path.join(root, "@eaDir"))
        # 建立一個檔案（不應出現在結果中）
        with open(os.path.join(root, "file.txt"), "w") as f:
            f.write("test")
        yield root


@pytest.fixture
def path_service(setting_service):
    """建立 DirectoryService 實例"""
    return DirectoryService(setting_service=setting_service)


class TestDirectoryServiceListDirectories:
    """測試 DirectoryService.list_directories 方法"""

    def test_list_directories_returns_subdirectories(
        self, path_service, setting_service, db_session, temp_dir_structure
    ):
        """測試回傳指定目錄下的子目錄列表（name, path, has_children）"""
        # 設定允許目錄
        setting = Setting(
            key="allowed_directories",
            value=json.dumps([temp_dir_structure]),
        )
        db_session.add(setting)
        db_session.commit()

        result = path_service.list_directories(temp_dir_structure)

        names = [d["name"] for d in result]
        assert "anime" in names
        assert "movies" in names
        # 檔案不應出現
        assert "file.txt" not in names

        # 檢查 has_children
        anime = next(d for d in result if d["name"] == "anime")
        assert anime["has_children"] is True

        movies = next(d for d in result if d["name"] == "movies")
        assert movies["has_children"] is False

    def test_list_directories_no_path_returns_root_directories(
        self, path_service, setting_service, db_session, temp_dir_structure
    ):
        """測試未提供 path 時回傳所有允許的根目錄"""
        setting = Setting(
            key="allowed_directories",
            value=json.dumps([temp_dir_structure]),
        )
        db_session.add(setting)
        db_session.commit()

        result = path_service.list_directories(None)

        assert len(result) == 1
        assert result[0]["path"] == temp_dir_structure

    def test_list_directories_access_denied(
        self, path_service, setting_service, db_session, temp_dir_structure
    ):
        """測試 path 不在允許目錄範圍內時拋出 403 錯誤"""
        setting = Setting(
            key="allowed_directories",
            value=json.dumps([temp_dir_structure]),
        )
        db_session.add(setting)
        db_session.commit()

        with pytest.raises(DirectoryAccessDenied):
            path_service.list_directories("/etc/secret")

    def test_list_directories_not_found(
        self, path_service, setting_service, db_session, temp_dir_structure
    ):
        """測試 path 不存在時拋出 404 錯誤"""
        nonexistent = os.path.join(temp_dir_structure, "nonexistent")
        setting = Setting(
            key="allowed_directories",
            value=json.dumps([temp_dir_structure]),
        )
        db_session.add(setting)
        db_session.commit()

        with pytest.raises(DirectoryNotFound):
            path_service.list_directories(nonexistent)

    def test_list_directories_path_traversal_attack(
        self, path_service, setting_service, db_session, temp_dir_structure
    ):
        """測試路徑遍歷攻擊防護（../  正規化後判斷）"""
        setting = Setting(
            key="allowed_directories",
            value=json.dumps([temp_dir_structure]),
        )
        db_session.add(setting)
        db_session.commit()

        # 嘗試路徑遍歷
        traversal_path = os.path.join(temp_dir_structure, "anime", "..", "..")
        with pytest.raises(DirectoryAccessDenied):
            path_service.list_directories(traversal_path)

    def test_list_directories_empty_when_no_allowed(
        self, path_service, setting_service
    ):
        """測試允許目錄未設定時回傳空列表"""
        result = path_service.list_directories(None)
        assert result == []

    def test_list_directories_excludes_hidden(
        self, path_service, setting_service, db_session, temp_dir_structure
    ):
        """測試排除隱藏目錄"""
        setting = Setting(
            key="allowed_directories",
            value=json.dumps([temp_dir_structure]),
        )
        db_session.add(setting)
        db_session.commit()

        result = path_service.list_directories(temp_dir_structure)
        names = [d["name"] for d in result]
        assert ".hidden" not in names

    def test_list_directories_excludes_hash_prefix(
        self, path_service, setting_service, db_session, temp_dir_structure
    ):
        """測試排除 # 開頭的系統目錄"""
        setting = Setting(
            key="allowed_directories",
            value=json.dumps([temp_dir_structure]),
        )
        db_session.add(setting)
        db_session.commit()

        result = path_service.list_directories(temp_dir_structure)
        names = [d["name"] for d in result]
        assert "#recycle" not in names

    def test_list_directories_excludes_at_prefix(
        self, path_service, setting_service, db_session, temp_dir_structure
    ):
        """測試排除 @ 開頭的系統目錄"""
        setting = Setting(
            key="allowed_directories",
            value=json.dumps([temp_dir_structure]),
        )
        db_session.add(setting)
        db_session.commit()

        result = path_service.list_directories(temp_dir_structure)
        names = [d["name"] for d in result]
        assert "@eaDir" not in names
