# core/services/task.py
from fastapi import HTTPException, status

from core import schemas
from core.repositories.task import TaskRepository


class TaskService:
    def __init__(self, repo: TaskRepository):
        self.repo = repo

    def get_all_tasks(self):
        return self.repo.get_all()

    def get_enabled_tasks(self):
        return self.repo.get_enabled_tasks()

    def create_task(self, task: schemas.TaskCreate):
        existing_task = self.repo.get_by_name(task.name)
        if existing_task:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task with this name already exists",
            )
        return self.repo.create(task)

    def update_task(self, task_id: str, task_update: schemas.TaskUpdate):
        db_task = self.repo.get_by_id(task_id)
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )

        # If name is being changed, check if the new name is already taken
        if task_update.name != db_task.name:
            existing_task = self.repo.get_by_name(task_update.name)
            if existing_task:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Another task with this name already exists",
                )

        return self.repo.update(task_id, task_update)

    def delete_task(self, task_id: str):
        db_task = self.repo.delete(task_id)
        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
            )
        return db_task

    def get_task_stats(self):
        return self.repo.get_stats()
