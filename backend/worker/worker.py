import os
from dataclasses import dataclass
from typing import Literal, Optional

from backend import schemas
from backend.database import SessionLocal
from backend.exceptions.workerException import MoveOperationError, RenameOperationError
from backend.repositories.log import LogRepository
from backend.repositories.task import TaskRepository
from backend.services.logService import LogService
from backend.services.taskService import TaskService
from backend.utils.move import move
from backend.utils.rename import Rename


@dataclass
class WorkerServices:
    """Worker 所需的服務容器"""

    task_service: TaskService
    log_service: LogService


# 延遲初始化的全域實例
_worker_services: Optional[WorkerServices] = None


def get_worker_services() -> WorkerServices:
    """獲取或建立 Worker 服務實例"""
    global _worker_services
    if _worker_services is None:
        db = SessionLocal()
        _worker_services = WorkerServices(
            task_service=TaskService(TaskRepository(db=db)),
            log_service=LogService(LogRepository(db=db)),
        )
    return _worker_services


def init_worker_services(services: WorkerServices) -> None:
    """初始化 Worker 服務（用於測試注入）"""
    global _worker_services
    _worker_services = services


def reset_worker_services() -> None:
    """重置 Worker 服務（用於測試清理）"""
    global _worker_services
    _worker_services = None


def web_logger(
    task_id: str,
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    message: str,
) -> None:
    """
    Webhook logger

    將 Webhook 事件記錄到日誌中

    :param task_id: 任務的 ID
    :param level: 日誌等級
    :param message: 日誌訊息
    """
    services = get_worker_services()
    services.log_service.create_log(
        schemas.LogCreate(
            task_id=task_id,
            level=level.upper(),
            message=message,
        )
    )


def match_task(tasks: list[schemas.Task], filepath: str) -> schemas.Task | None:
    """將路徑 filepath 與任務的 include 進行比對，找到第一個符合的任務

    Args:
        tasks: 任務列表
        filepath: 檔案的絕對路徑

    Returns:
        Task: 符合的任務，或 None 如果沒有符合
    """
    for task in tasks:
        if task.include in filepath:
            web_logger(
                task_id=task.id,
                level="INFO",
                message=f'檔案 "{os.path.basename(filepath)}" 與任務 "{task.name}" 匹配成功',
            )
            return task
    return None


def perform_rename_operation(task: schemas.Task, filepath: str) -> str:
    """
    將檔案重新命名，並返回重新命名後的路徑

    Args:
        task: 任務
        filepath: 檔案的絕對路徑

    Returns:
        str: 重新命名後的檔案路徑

    Raises:
        RenameOperationError: 重命名操作失敗時
    """
    if task.rename_rule is None:
        return filepath

    try:
        dst_filepath = Rename(
            filepath=filepath,
            src=task.src_filename,
            dst=task.dst_filename,
            rule=task.rename_rule,
        ).execute_rename()

        web_logger(
            task_id=task.id,
            level="INFO",
            message=f'檔案 "{os.path.basename(filepath)}" 重新命名為 "{os.path.basename(dst_filepath)}" 成功',
        )
        return dst_filepath
    except (OSError, ValueError) as e:
        web_logger(
            task_id=task.id,
            level="ERROR",
            message=f'檔案 "{os.path.basename(filepath)}" 重新命名失敗，錯誤訊息: {str(e)}',
        )
        raise RenameOperationError(filepath, str(e)) from e


def perform_move_operation(task: schemas.Task, filepath: str) -> None:
    """
    將檔案移動到指定的目錄

    Args:
        task: 任務
        filepath: 檔案的絕對路徑

    Raises:
        MoveOperationError: 移動操作失敗時
    """
    try:
        move(filepath, task.move_to)
        web_logger(
            task_id=task.id,
            level="INFO",
            message=f'檔案 "{os.path.basename(filepath)}" 移動至 "{task.move_to}" 成功',
        )
    except OSError as e:
        web_logger(
            task_id=task.id,
            level="ERROR",
            message=f'檔案 "{os.path.basename(filepath)}" 移動至 "{task.move_to}" 失敗，錯誤訊息: {str(e)}',
        )
        raise MoveOperationError(filepath, task.move_to, str(e)) from e


def process_completed_download(filepath: str) -> None:
    """
    處理已完成的下載任務

    這個方法會根據已完成的下載檔案名稱，尋找相符的任務。
    如果找到相符的任務，則會執行重新命名和移動檔案。

    Args:
        filepath: 檔案的絕對路徑
    """
    services = get_worker_services()
    tasks = services.task_service.get_enabled_tasks()

    task = match_task(tasks, filepath)
    if task is None:
        return  # 沒有匹配的任務，直接返回

    try:
        dst_filepath = perform_rename_operation(task, filepath)
        perform_move_operation(task, dst_filepath)
    except RenameOperationError:
        # 重命名失敗，不執行移動操作（已記錄日誌）
        return
    except MoveOperationError:
        # 移動失敗（已記錄日誌）
        return
