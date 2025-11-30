from backend import schemas
from backend.repositories.log import LogRepository


class LogService:
    def __init__(self, repository: LogRepository):
        self.repository = repository

    def get_logs_by_task_id(self, task_id: str):
        return self.repository.get_by_task_id(task_id)

    def create_log(self, log: schemas.LogCreate):
        return self.repository.create(log)
