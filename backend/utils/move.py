import shutil
from pathlib import Path


def move(filepath: str | Path, dst_path: str | Path) -> None:
    """
    移動檔案至指定的目標資料夾。

    Args:
        filepath (str | Path): 原始檔案的路徑。
        dst_path (str | Path): 目標資料夾的路徑。

    Returns:
        None
    """
    if isinstance(filepath, str):
        filepath = Path(filepath)
    if isinstance(dst_path, str):
        dst_path = Path(dst_path)
    if dst_path.is_dir() is False:
        dst_path.mkdir(parents=True, exist_ok=True)
    shutil.move(filepath, dst_path)
