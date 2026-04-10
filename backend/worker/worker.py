import os
from dataclasses import dataclass
from typing import Literal

from backend import schemas
from backend.database import SessionLocal
from backend.exceptions.worker_exception import MoveOperationError, RenameOperationError
from backend.repositories.log import LogRepository
from backend.repositories.task import TaskRepository
from backend.services.log_service import LogService
from backend.services.task_service import TaskService
from backend.utils.move import move
from backend.utils.rename import Rename


@dataclass
class WorkerServices:
    """Worker 所需的服務容器。

    Why: 將 Worker 依賴的服務封裝為資料類別，
    讓服務可透過參數傳入而非全域狀態，提升可測試性與執行緒安全性。
    """

    task_service: TaskService
    log_service: LogService


def create_worker_services() -> WorkerServices:
    """建立 Worker 服務實例。

    Why: 將服務建立邏輯集中在此工廠函式，
    讓呼叫端（webhook 路由）負責生命週期管理。
    """
    db = SessionLocal()
    return WorkerServices(
        task_service=TaskService(TaskRepository(db=db)),
        log_service=LogService(LogRepository(db=db)),
    )


def web_logger(
    services: WorkerServices,
    task_id: str,
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    message: str,
) -> None:
    """將 Webhook 事件記錄到日誌中。

    :param services: Worker 服務容器
    :param task_id: 任務的 ID
    :param level: 日誌等級
    :param message: 日誌訊息
    """
    services.log_service.create_log(
        schemas.LogCreate(
            task_id=task_id,
            level=level.upper(),
            message=message,
        )
    )


def match_task(
    services: WorkerServices,
    tasks: list[schemas.Task],
    filepath: str,
) -> schemas.Task | None:
    """將路徑 filepath 與任務的 include 進行比對，找到第一個符合的任務。

    Why: 比對邏輯獨立於 process_completed_download，
    讓單元測試可以單獨驗證比對行為。

    Args:
        services: Worker 服務容器
        tasks: 任務列表
        filepath: 檔案的絕對路徑

    Returns:
        符合的任務，或 None 如果沒有符合
    """
    for task in tasks:
        if task.include in filepath:
            web_logger(
                services=services,
                task_id=task.id,
                level="INFO",
                message=f'檔案 "{os.path.basename(filepath)}" 與任務 "{task.name}" 匹配成功',
            )
            return task
    return None


def perform_rename_operation(
    services: WorkerServices,
    task: schemas.Task,
    filepath: str,
) -> str:
    """將檔案重新命名，並返回重新命名後的路徑。

    Args:
        services: Worker 服務容器
        task: 任務
        filepath: 檔案的絕對路徑

    Returns:
        重新命名後的檔案路徑

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
            services=services,
            task_id=task.id,
            level="INFO",
            message=f'檔案 "{os.path.basename(filepath)}" 重新命名為 "{os.path.basename(dst_filepath)}" 成功',
        )
        return dst_filepath
    except (OSError, ValueError) as e:
        web_logger(
            services=services,
            task_id=task.id,
            level="ERROR",
            message=f'檔案 "{os.path.basename(filepath)}" 重新命名失敗，錯誤訊息: {str(e)}',
        )
        raise RenameOperationError(filepath, str(e)) from e


def perform_move_operation(
    services: WorkerServices,
    task: schemas.Task,
    filepath: str,
) -> None:
    """將檔案移動到指定的目錄。

    Args:
        services: Worker 服務容器
        task: 任務
        filepath: 檔案的絕對路徑

    Raises:
        MoveOperationError: 移動操作失敗時
    """
    try:
        move(filepath, task.move_to)
        web_logger(
            services=services,
            task_id=task.id,
            level="INFO",
            message=f'檔案 "{os.path.basename(filepath)}" 移動至 "{task.move_to}" 成功',
        )
    except OSError as e:
        web_logger(
            services=services,
            task_id=task.id,
            level="ERROR",
            message=f'檔案 "{os.path.basename(filepath)}" 移動至 "{task.move_to}" 失敗，錯誤訊息: {str(e)}',
        )
        raise MoveOperationError(filepath, task.move_to, str(e)) from e


def process_completed_download(filepath: str, services: WorkerServices | None = None) -> None:
    """處理已完成的下載任務。

    Why: 接受可選的 services 參數，讓測試可以注入 mock 服務，
    同時保持向後相容性——未傳入時自動建立服務實例。

    Args:
        filepath: 檔案的絕對路徑
        services: Worker 服務容器（可選，未提供時自動建立）
    """
    if services is None:
        services = create_worker_services()

    tasks = services.task_service.get_enabled_tasks()

    task = match_task(services, tasks, filepath)
    if task is None:
        return

    try:
        dst_filepath = perform_rename_operation(services, task, filepath)
        perform_move_operation(services, task, dst_filepath)
    except RenameOperationError:
        return
    except MoveOperationError:
        return
