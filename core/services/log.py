# core/services/log.py
from core import schemas
from core.repositories.log import LogRepository


class LogService:
    def __init__(self, repo: LogRepository):
        self.repo = repo

    def get_logs_for_task(self, task_id: str):
        return self.repo.get_by_task_id(task_id)

    def create_log(self, log: schemas.LogCreate):
        # In a real app, you might want to check if the task_id exists first
        return self.repo.create(log)
