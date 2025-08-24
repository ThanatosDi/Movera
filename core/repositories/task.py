# core/repositories/task.py
from sqlalchemy import func
from sqlalchemy.orm import Session

from core import models, schemas


class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, task_id: str) -> models.Task | None:
        """取得指定 id 的任務

        Args:
            task_id (str): 任務的 id

        Returns:
            models.Task | None: 該任務或 None (如果不存在)
        """
        return self.db.query(models.Task).filter(models.Task.id == task_id).first()

    def get_by_name(self, name: str) -> models.Task | None:
        """取得指定名稱的任務

        Args:
            name (str): 任務的名稱

        Returns:
            models.Task | None: 該任務或 None (如果不存在)
        """
        return self.db.query(models.Task).filter(models.Task.name == name).first()

    def get_all(self) -> list[models.Task]:
        """取得所有任務

        Returns:
            list[models.Task]: 所有任務清單
        """
        return self.db.query(models.Task).all()

    def create(self, task: schemas.TaskCreate) -> models.Task:
        """新增一個任務

        Args:
            task (schemas.TaskCreate): 任務的資料

        Returns:
            models.Task: 剛才建立的任務
        """
        db_task = models.Task(**task.model_dump())
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def update(
        self, task_id: str, task_update: schemas.TaskUpdate
    ) -> models.Task | None:
        """更新一個任務

        Args:
            task_id (str): 任務的 ID
            task_update (schemas.TaskUpdate): 任務的更新資料

        Returns:
            models.Task | None: 該任務或 None (如果不存在)
        """
        db_task = self.get_by_id(task_id)
        if db_task:
            update_data = task_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_task, key, value)
            self.db.commit()
            self.db.refresh(db_task)
        return db_task

    def delete(self, task_id: str) -> models.Task | None:
        """刪除一個任務

        Args:
            task_id (str): 任務的 ID

        Returns:
            models.Task | None: 該任務或 None (如果不存在)
        """
        db_task = self.get_by_id(task_id)
        if db_task:
            self.db.delete(db_task)
            self.db.commit()
        return db_task

    def get_stats(self) -> schemas.TaskStats:
        """取得任務的啟用狀態統計資料

        Returns:
            schemas.TaskStats: 任務的啟用狀態統計資料
        """
        results = (
            self.db.query(models.Task.enabled, func.count(models.Task.id))
            .group_by(models.Task.enabled)
            .all()
        )

        stats = schemas.TaskStats()
        for enabled, count in results:
            if enabled:
                stats.enabled = count
            else:
                stats.disabled = count
        return stats

    def get_enabled_tasks(self) -> list[schemas.Task]:
        """取得所有已啟用的任務

        Returns:
            list[schemas.Task]: 已啟用的任務清單
        """
        return self.db.query(models.Task).filter(models.Task.enabled.is_(True)).all()
