from sqlalchemy.orm import Session
from api.models.database import TaskTagMapping, Task, Tag

class TaskTagMappingRepository:
    def get_tags_by_task(self, session: Session, task_id: str):
        task = session.get(Task, task_id)
        return task.tags if task else []

    def create(self, session: Session, task_id: str, tag_id: int):
        task = session.get(Task, task_id)
        tag = session.get(Tag, tag_id)

        if not task or not tag:
            return None # Or raise an exception

        task.tags.append(tag)
        session.commit()
        return task

    def delete(self, session: Session, task_id: str, tag_id: int):
        task = session.get(Task, task_id)
        tag = session.get(Tag, tag_id)

        if not task or not tag:
            return None # Or raise an exception

        try:
            task.tags.remove(tag)
            session.commit()
            return True
        except ValueError:
            return False # Tag was not associated with the task
