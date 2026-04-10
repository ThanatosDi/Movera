"""路徑驗證工具函式。

Why: 路徑驗證邏輯被 SettingService 和 DirectoryService 共用，
提取為獨立模組避免重複且確保驗證行為一致。
"""

from pathlib import PurePosixPath, PureWindowsPath


def is_absolute_path(path: str) -> bool:
    """檢查路徑是否為絕對路徑（支援 POSIX 和 Windows）。

    Why: 需要同時支援 Linux/macOS 的 POSIX 路徑與 Windows 路徑格式，
    因此使用兩種 Pure 路徑類別進行檢查。
    """
    return PurePosixPath(path).is_absolute() or PureWindowsPath(path).is_absolute()


def validate_allowed_directories(directories: list[str]) -> list[str]:
    """驗證允許目錄列表，僅接受絕對路徑。

    Returns:
        無效路徑列表（非絕對路徑）
    """
    return [d for d in directories if not is_absolute_path(d)]
