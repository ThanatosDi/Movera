"""
Utils move 模組單元測試
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import os

from backend.utils.move import move


class TestMove:
    """測試 move 函數"""

    def test_move_file_to_existing_dir(self, tmp_path):
        """測試移動檔案到現有目錄"""
        # 建立來源檔案
        src_file = tmp_path / "source" / "test.txt"
        src_file.parent.mkdir(parents=True, exist_ok=True)
        src_file.write_text("test content")

        # 建立目標目錄
        dst_dir = tmp_path / "destination"
        dst_dir.mkdir(parents=True, exist_ok=True)

        # 執行移動
        move(str(src_file), str(dst_dir))

        # 驗證
        assert not src_file.exists()
        assert (dst_dir / "test.txt").exists()
        assert (dst_dir / "test.txt").read_text() == "test content"

    def test_move_file_to_non_existing_dir(self, tmp_path):
        """測試移動檔案到不存在的目錄 (會自動建立)"""
        # 建立來源檔案
        src_file = tmp_path / "source" / "test.txt"
        src_file.parent.mkdir(parents=True, exist_ok=True)
        src_file.write_text("test content")

        # 目標目錄不存在
        dst_dir = tmp_path / "new_destination" / "nested"

        # 執行移動
        move(str(src_file), str(dst_dir))

        # 驗證 - 目錄應該被自動建立
        assert dst_dir.exists()
        assert (dst_dir / "test.txt").exists()

    def test_move_with_path_objects(self, tmp_path):
        """測試使用 Path 物件"""
        # 建立來源檔案
        src_file = tmp_path / "source" / "test.txt"
        src_file.parent.mkdir(parents=True, exist_ok=True)
        src_file.write_text("test content")

        dst_dir = tmp_path / "destination"
        dst_dir.mkdir(parents=True, exist_ok=True)

        # 使用 Path 物件
        move(src_file, dst_dir)

        # 驗證
        assert not src_file.exists()
        assert (dst_dir / "test.txt").exists()

    def test_move_with_string_paths(self, tmp_path):
        """測試使用字串路徑"""
        # 建立來源檔案
        src_file = tmp_path / "source" / "test.txt"
        src_file.parent.mkdir(parents=True, exist_ok=True)
        src_file.write_text("test content")

        dst_dir = tmp_path / "destination"
        dst_dir.mkdir(parents=True, exist_ok=True)

        # 使用字串
        move(str(src_file), str(dst_dir))

        # 驗證
        assert not src_file.exists()
        assert (dst_dir / "test.txt").exists()

    def test_move_preserves_content(self, tmp_path):
        """測試移動後檔案內容保持不變"""
        # 建立有內容的檔案
        src_file = tmp_path / "source" / "data.txt"
        src_file.parent.mkdir(parents=True, exist_ok=True)
        original_content = "這是測試內容\n包含多行\n以及中文"
        src_file.write_text(original_content, encoding="utf-8")

        dst_dir = tmp_path / "destination"
        dst_dir.mkdir(parents=True, exist_ok=True)

        move(src_file, dst_dir)

        # 驗證內容
        moved_file = dst_dir / "data.txt"
        assert moved_file.read_text(encoding="utf-8") == original_content

    def test_move_creates_nested_directories(self, tmp_path):
        """測試自動建立多層巢狀目錄"""
        src_file = tmp_path / "test.txt"
        src_file.write_text("content")

        # 多層巢狀目錄
        dst_dir = tmp_path / "level1" / "level2" / "level3"

        move(src_file, dst_dir)

        assert dst_dir.exists()
        assert (dst_dir / "test.txt").exists()
