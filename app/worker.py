from app.modules.move import move
from app.modules.rename import Rename
from core import schemas
from core.database import SessionLocal
from core.repositories.log import LogRepository
from core.repositories.task import TaskRepository
from core.schemas.task import Task
from core.services.log import LogService
from core.services.task import TaskService
from core.utils.logger import logger as _logger

db = SessionLocal()
task_service = TaskService(TaskRepository(db))
log_service = LogService(LogRepository(db))
logger = _logger.bind(app="worker")


def match_task(tasks: list[Task], task_includes: list, filepath: str) -> Task | None:
    """將路徑 filepath 與 task_includes 列表進行比對，找到第一個符合的任務
    Args:
        tasks (list): 任務列表
        task_includes (list): 任務列表的 include
        filepath (str): 檔案的絕對路徑
    Returns:
        Task: 符合的任務
        None: 沒有符合的任務
    """
    for index, include in enumerate(task_includes, start=0):
        if include in filepath:
            task = tasks[index]
            log_service.create_log(
                schemas.LogCreate(
                    task_id=task.id,
                    level="INFO",
                    message=f"檔案 \"{filepath}\" 匹配到任務 '{task.name}'",
                )
            )
            return task
    return None


def perform_rename_operation(task: Task, filepath: str):
    """
    將檔案重新命名，並返回重新命名後的路徑

    Args:
        task (Task): 任務
        filepath (str): 檔案的絕對路徑

    Returns:
        str: 重新命名後的檔案路徑
    """

    try:
        dst_filepath = Rename(
            filepath=filepath,
            src=task.src_filename,
            dst=task.dst_filename,
            rule=task.rename_rule,
        ).execute_rename()
        return dst_filepath
    except Exception as e:
        log_service.create_log(
            schemas.LogCreate(
                task_id=task.id,
                level="ERROR",
                message=f'檔案 "{filepath}" 重新命名失敗，錯誤訊息: {str(e)}',
            )
        )


def perform_move_operation(task: Task, filepath: str):
    """
    將檔案移動到指定的目錄

    Args:
        task (Task): 任務
        filepath (str): 檔案的絕對路徑
    """
    try:
        move(filepath, task.move_to)
    except Exception as e:
        log_service.create_log(
            schemas.LogCreate(
                task_id=task.id,
                level="ERROR",
                message=f'檔案 "{filepath}" 移動至 "{task.move_to}" 失敗，錯誤訊息: {str(e)}',
            )
        )


def process_completed_download(filepath: str):
    tasks = task_service.get_enabled_tasks()
    task_includes = [task.include for task in tasks]

    task = match_task(tasks, task_includes, filepath)
    if task is None:
        return  # 沒有匹配的任務，直接返回
    dst_filepath = perform_rename_operation(task, filepath)
    perform_move_operation(task, dst_filepath)
