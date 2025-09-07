from datetime import date

import arrow
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from api.models.database import Log
from api.utils.tools import deprecated


class LogRepository:
    def get_task_log(self, session: Session, task_id: str):
        return session.scalars(
            select(Log).where(Log.task_id == task_id).order_by(Log.timestamp.desc())
        ).all()

    @deprecated("get_by_task_id is deprecated, use get_task_log instead")
    def get_by_task_id(self, session: Session, task_id: str):
        return session.scalars(
            select(Log).where(Log.task_id == task_id).order_by(Log.timestamp.desc())
        ).all()

    def create(self, session: Session, log: Log):
        session.add(log)
        session.commit()
        return log

    def delete_log_by_id(self, session: Session, log_id: int) -> int:
        result = session.execute(delete(Log).where(Log.id == log_id))
        session.commit()
        return result.rowcount

    def delete_logs_before_date(self, session: Session, before_date: date) -> int:
        result = session.execute(delete(Log).where(Log.timestamp < before_date))
        session.commit()
        return result.rowcount


