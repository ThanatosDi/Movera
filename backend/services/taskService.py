from backend import models, schemas
from backend.exceptions.taskException import (
    TaskAlreadyExists,
    TaskNotFound,
)
from backend.repositories.task import TaskRepository
from backend.utils.logger import logger


class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def _get_task_or_raise(self, task_id: str) -> models.Task:
        """
        獲取任務，若不存在則拋出 TaskNotFound

        Args:
            task_id (str): 任務的 ID

        Returns:
            models.Task: 該任務

        Raises:
            TaskNotFound: 如果不存在相同ID的任務
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            raise TaskNotFound(task_id)
        return task

    def get_all_tasks(self) -> list[models.Task | None]:
        """
        取得所有任務

        Returns:
            list[models.Task | None]: 所有任務清單
        """
        return self.repository.get_all()

    def get_enabled_tasks(self) -> list[models.Task | None]:
        """
        取得所有啟用的任務

        Returns:
            list[models.Task | None]: 所有啟用的任務清單
        """
        return self.repository.get_enabled_tasks()

    def get_task_by_id(self, task_id: str) -> models.Task | None:
        """
        取得指定 id 的任務

        Args:
            task_id (str): 任務的 id

        Returns:
            models.Task | None: 該任務或 None (如果不存在)
        """
        return self.repository.get_by_id(task_id)

    def get_task_by_name(self, name: str) -> models.Task | None:
        """
        取得指定名稱的任務

        Args:
            name (str): 任務的名稱

        Returns:
            models.Task | None: 該任務或 None (如果不存在)
        """
        return self.repository.get_by_name(name)

    def create_task(
        self,
        task: schemas.TaskCreate,
    ) -> models.Task:
        """
        創建一個任務

        Args:
            task (schemas.TaskCreate): 任務的資料

        Returns:
            models.Task: 剛才建立的任務

        Raises:
            TaskAlreadyExists: 如果已經存在相同名稱的任務
        """
        exists_task = self.get_task_by_name(task.name)
        if exists_task is not None:
            raise TaskAlreadyExists(task.name)
        return self.repository.create(task)

    def update_task(
        self,
        task_id: str,
        task_update: schemas.TaskUpdate,
    ) -> models.Task:
        """
        更新一個任務

        Args:
            task_id (str): 任務的 ID
            task_update (schemas.TaskUpdate): 任務的更新資料

        Returns:
            models.Task: 該任務

        Raises:
            TaskNotFound: 如果不存在相同ID的任務
            TaskAlreadyExists: 如果已經存在相同名稱的任務
        """
        exists_task = self._get_task_or_raise(task_id)
        if exists_task.name != task_update.name:
            same_name_task = self.get_task_by_name(task_update.name)
            if same_name_task is not None:
                raise TaskAlreadyExists(task_update.name)
        return self.repository.update(task_id, task_update)

    def delete_task(self, task_id: str) -> models.Task:
        """
        刪除一個任務

        Args:
            task_id (str): 任務的 ID

        Returns:
            models.Task: 該任務

        Raises:
            TaskNotFound: 如果不存在相同ID的任務
        """
        self._get_task_or_raise(task_id)
        return self.repository.delete(task_id)
