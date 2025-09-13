# core/services/log.py
from core import schemas
from core.repositories.log import LogRepository
from core.repositories.setting import SettingRepository
from core.services.setting import SettingService
from core.utils.timezone import utc_to_local


class LogService:
    def __init__(self, repo: LogRepository):
        self.repo = repo
        self.setting_service = SettingService(SettingRepository())

    def get_logs_for_task(self, task_id: str):
        task_logs = self.repo.get_by_task_id(task_id)
        timezone = self.setting_service.get_setting("timezone").value
        for task_log in task_logs:
            task_log.timestamp = utc_to_local(task_log.timestamp, timezone)
        return task_logs

    def create_log(self, log: schemas.LogCreate):
        # In a real app, you might want to check if the task_id exists first
        return self.repo.create(log)
