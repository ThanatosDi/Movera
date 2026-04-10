
from sqlalchemy.orm import Session

from backend import models
from backend.schemas import LogCreate


class LogRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_task_id(self, task_id: str) -> list[models.Log]:
        return self.db.query(models.Log).filter(models.Log.task_id == task_id).order_by(models.Log.timestamp.desc()).all()

    def create(self, log: LogCreate) -> models.Log:
        db_log = models.Log(**log.model_dump())
        self.db.add(db_log)
        self.db.commit()
        self.db.refresh(db_log)
        return db_log
