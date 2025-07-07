import os
import re
import shutil
import time
from pathlib import Path

import yaml
from loguru import logger

from app.model import Config, Job


def read_config(config_yaml_path: str | Path) -> Config:
    """
    讀取 YAML 設定檔案並返回 Config 對象。

    Args:
        config_yaml_path (str | Path): 設定檔案的路徑。

    Returns:
        Config: 包含監控和任務訊息的物件。
    """

    config = yaml.safe_load(open(config_yaml_path, "r", encoding="utf-8"))
    return Config(watches=config["watches"], jobs=config["jobs"], log=config["log"])


def is_file_stable(
    src_path: str | Path, check_interval: float = 1.0, stable_checks: int = 3
):
    """
    NFS 環境下判斷檔案是否穩定：
    連續 stable_checks 次檢查檔案大小不變
    """
    if isinstance(src_path, str):
        src_path = Path(src_path)
    if not src_path.is_file():
        return False

    stable_count = 0
    file_stat = src_path.stat()

    last_size = file_stat.st_size

    while stable_count < stable_checks:
        time.sleep(check_interval)
        try:
            current_size = os.path.getsize(src_path)
        except FileNotFoundError:
            return False
        if current_size == last_size:
            stable_count += 1
        else:
            stable_count = 0
            last_size = current_size
    return True


def wait_until_file_stable(
    filepath: str | Path, stable_seconds: int = 3, check_interval: int = 1
):
    """
    等待檔案穩定 (不再增長) 後返回 True

    Args:
        filepath (str | Path): 檔案路徑
        stable_seconds (int): 檔案穩定需要的秒數
        check_interval (int): 檢查檔案大小的間隔秒數

    Returns:
        bool: 檔案是否穩定
    """
    last_size = -1
    stable_time = 0
    retry_time = 0
    while True:
        try:
            size = os.path.getsize(filepath)
        except FileNotFoundError:
            # 檔案可能還沒完全寫入
            logger.debug(f"檔案不存在: {filepath}")
            time.sleep(check_interval)
            retry_time += 1
            if retry_time >= 5:
                return False
            continue
        if size == last_size:
            stable_time += check_interval
            if stable_time >= stable_seconds:
                return True
        else:
            stable_time = 0
        last_size = size
        time.sleep(check_interval)


def match_job(filename: str, config: Config) -> Job | None:
    """
    尋找第一個符合 filename 的 Job。

    Args:
        filename (str): 檔案名稱
        config (Config): 設定物件

    Returns:
        Job | None: 符合的 Job 或 None
    """
    for job in config.jobs:
        logger.debug(f"比對: {job}")
        if config.jobs[job].include in filename:
            logger.info(f"比對成功: {job}")
            return config.jobs[job]
        else:
            continue
    return None


def rename(src_path: str | Path, job: Job) -> Path:
    """
    根據提供的 Job 將檔案重新命名。

    Args:
        src_path (str | Path): 原始檔案的路徑。
        job (Job): 包含檔案重命名規則的 Job 物件。

    Returns:
        Path: 重新命名後檔案的新路徑。
    """
    if isinstance(src_path, str):
        src_path = Path(src_path)
    filename = src_path.name
    src_filename_regex = re.compile(job.src_filename_regex, re.IGNORECASE)
    renamed = re.sub(src_filename_regex, job.dst_filename_regex, filename)
    dst_path = src_path.parent.joinpath(renamed)
    return Path.rename(src_path, dst_path)


def move(src_path: str | Path, job: Job):
    """
    移動檔案至指定的目標資料夾。

    Args:
        src_path (str | Path): 原始檔案的路徑。
        job (Job): 包含目標資料夾資訊的 Job 物件。

    Returns:
        None
    """
    if isinstance(src_path, str):
        src_path = Path(src_path)
    dst = job.move_to
    shutil.move(src_path, dst)
