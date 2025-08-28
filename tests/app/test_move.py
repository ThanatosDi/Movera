from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from app.modules.move import move


@pytest.fixture
def filepath(tmp_path: Path | str) -> Path:
    return "/mnt/storage/2025 夏番/公爵千金的家庭教師/"


def test_move_creates_dir_and_moves_when_dst_missing(
    mocker: MockerFixture, tmp_path: Path
):
    """當目標資料夾不存在時，應建立資料夾並執行移動。"""
    src = tmp_path / "file.txt"
    dst = tmp_path / "dest"

    move_mock = mocker.patch("app.modules.move.shutil.move")
    mocker.patch.object(Path, "is_dir", return_value=False)
    mkdir_mock = mocker.patch.object(Path, "mkdir")

    # 傳入字串參數以覆蓋 str 與 Path 的分支
    move(str(src), str(dst))

    mkdir_mock.assert_called_once_with(parents=True, exist_ok=True)
    move_mock.assert_called_once_with(src, dst)


def test_move_skips_mkdir_when_dst_exists(mocker: MockerFixture, tmp_path: Path):
    """當目標資料夾已存在時，不應呼叫 mkdir，但仍需移動。"""
    src = tmp_path / "file.txt"
    dst = tmp_path / "dest"

    move_mock = mocker.patch("app.modules.move.shutil.move")
    mocker.patch.object(Path, "is_dir", return_value=True)
    mkdir_mock = mocker.patch.object(Path, "mkdir")

    # 傳入 Path 參數
    move(src, dst)

    mkdir_mock.assert_not_called()
    move_mock.assert_called_once_with(src, dst)
