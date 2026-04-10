from backend import models, schemas
from backend.repositories.log import LogRepository


class LogService:
    """Persistence layer for task execution logs.

    Why: Keeps log creation and querying behind a service boundary so that
    the worker and routers share consistent logging behaviour.
    """

    def __init__(self, repository: LogRepository):
        self.repository = repository

    def get_logs_by_task_id(self, task_id: str) -> list[models.Log]:
        return self.repository.get_by_task_id(task_id)

    def create_log(self, log: schemas.LogCreate) -> models.Log:
        return self.repository.create(log)
