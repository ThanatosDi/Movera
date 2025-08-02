from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.orm.exc import NoResultFound

from api.models.database import Task


class TaskRepository:
    def get_all(self, session: Session):
        return session.scalars(
            select(Task)
            .options(selectinload(Task.tags))
            .options(selectinload(Task.logs))
        ).all()

    def get(self, session: Session, task_id: str):
        task = session.scalars(select(Task).where(Task.id == task_id)).one_or_none()
        return task

    def create(self, session: Session, task: Task):
        session.add(task)
        session.commit()

    def update(self, session: Session, task_id: str, task: Task):
        exist_task = session.scalars(
            select(Task).where(Task.id == task_id)
        ).one_or_none()
        if exist_task is None:
            raise NoResultFound(f"Task {task_id} not found")

        exist_task.name = task.name
        exist_task.include = task.include
        exist_task.move_to = task.move_to
        exist_task.src_filename_regex = task.src_filename_regex
        exist_task.dst_filename_regex = task.dst_filename_regex
        session.add(exist_task)
        session.commit()

    def delete(self, session: Session, task_id: str):
        task = session.scalars(select(Task).where(Task.id == task_id)).one()
        if task:
            session.delete(task)
            session.commit()

    def all_status(self, session: Session) -> dict[str, int]:
        tasks = session.scalars(select(Task.enabled)).all()
        enabled = tasks.count(True)
        disabled = tasks.count(False)
        return {"enabled": enabled, "disabled": disabled}
