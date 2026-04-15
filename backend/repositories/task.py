from typing import Sequence

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend import models
from backend.exceptions.task_exception import TaskAlreadyExists, TaskNotFound
from backend.schemas import Task, TaskBatchUpdateItem, TaskCreate, TaskStats, TaskUpdate


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

    def create(self, task: TaskCreate) -> models.Task:
        """新增一個任務

        Args:
            task (schemas.TaskCreate): 任務的資料

        Returns:
            models.Task: 剛才建立的任務
        """
        tag_ids = task.tag_ids if hasattr(task, "tag_ids") else []
        db_task = models.Task(**task.model_dump(exclude={"tag_ids"}))
        if tag_ids:
            tags = self.db.query(models.Tag).filter(models.Tag.id.in_(tag_ids)).all()
            db_task.tags = tags
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def update(self, task_id: str, task_update: TaskUpdate) -> models.Task | None:
        """更新一個任務

        Args:
            task_id (str): 任務的 ID
            task_update (schemas.TaskUpdate): 任務的更新資料

        Returns:
            models.Task | None: 該任務或 None (如果不存在)
        """
        db_task = self.get_by_id(task_id)
        if db_task:
            update_data = task_update.model_dump(exclude_unset=True, exclude={"tag_ids"})
            for key, value in update_data.items():
                setattr(db_task, key, value)
            if hasattr(task_update, "tag_ids"):
                tags = self.db.query(models.Tag).filter(models.Tag.id.in_(task_update.tag_ids)).all()
                db_task.tags = tags
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

    def get_stats(self) -> TaskStats:
        """取得任務的啟用狀態統計資料

        Returns:
            schemas.TaskStats: 任務的啟用狀態統計資料
        """
        results = (
            self.db.query(models.Task.enabled, func.count(models.Task.id))
            .group_by(models.Task.enabled)
            .all()
        )

        stats = TaskStats()
        for enabled, count in results:
            if enabled:
                stats.enabled = count
            else:
                stats.disabled = count
        return stats

    def get_enabled_tasks(self) -> list[Task]:
        """取得所有已啟用的任務

        Returns:
            list[schemas.Task]: 已啟用的任務清單
        """
        return self.db.query(models.Task).filter(models.Task.enabled.is_(True)).all()

    # --- Batch operations ---

    def batch_create(self, items: list[TaskCreate]) -> list[models.Task]:
        """批量建立任務（單一交易，全成功或全回滾）

        Args:
            items: 要建立的 TaskCreate 清單

        Returns:
            list[models.Task]: 已建立的 ORM 物件清單（保持輸入順序）

        Raises:
            TaskAlreadyExists: 批量內重名，或與資料庫現有任務重名
        """
        # 檢查批量內部重名
        seen_names: set[str] = set()
        for item in items:
            if item.name in seen_names:
                raise TaskAlreadyExists(item.name)
            seen_names.add(item.name)

        # 檢查與資料庫現有任務重名
        names = list(seen_names)
        if names:
            existing = (
                self.db.query(models.Task.name)
                .filter(models.Task.name.in_(names))
                .all()
            )
            if existing:
                raise TaskAlreadyExists(existing[0][0])

        created: list[models.Task] = []
        try:
            for item in items:
                tag_ids = item.tag_ids if hasattr(item, "tag_ids") else []
                db_task = models.Task(**item.model_dump(exclude={"tag_ids"}))
                if tag_ids:
                    tags = (
                        self.db.query(models.Tag)
                        .filter(models.Tag.id.in_(tag_ids))
                        .all()
                    )
                    db_task.tags = tags
                self.db.add(db_task)
                created.append(db_task)
            self.db.commit()
            for db_task in created:
                self.db.refresh(db_task)
            return created
        except Exception:
            self.db.rollback()
            raise

    def batch_update(self, items: list[TaskBatchUpdateItem]) -> list[models.Task]:
        """批量更新任務（單一交易，全成功或全回滾）

        Args:
            items: 批量更新項目清單（每筆包含 id 與 patch）

        Returns:
            list[models.Task]: 已更新的 ORM 物件清單（保持輸入順序）

        Raises:
            TaskNotFound: 任一 id 在資料庫中不存在
            TaskAlreadyExists: 更新後的名稱與其他任務重名
        """
        # 一次查詢驗證全部存在
        ids = [item.id for item in items]
        existing_map = {
            t.id: t
            for t in self.db.query(models.Task).filter(models.Task.id.in_(ids)).all()
        }
        for item in items:
            if item.id not in existing_map:
                raise TaskNotFound(item.id)

        # 收集 patch 中的新名稱做 intra-batch 衝突檢查
        patch_name_to_ids: dict[str, str] = {}
        for item in items:
            new_name = item.patch.name
            if new_name is None:
                continue
            if new_name in patch_name_to_ids and patch_name_to_ids[new_name] != item.id:
                raise TaskAlreadyExists(new_name)
            patch_name_to_ids[new_name] = item.id

        # 與資料庫現有其他任務重名檢查
        if patch_name_to_ids:
            conflict = (
                self.db.query(models.Task)
                .filter(
                    models.Task.name.in_(list(patch_name_to_ids.keys())),
                    models.Task.id.notin_(ids),
                )
                .first()
            )
            if conflict is not None:
                raise TaskAlreadyExists(conflict.name)

        updated: list[models.Task] = []
        try:
            for item in items:
                db_task = existing_map[item.id]
                patch_data = item.patch.model_dump(exclude_unset=True, exclude={"tag_ids"})
                for key, value in patch_data.items():
                    setattr(db_task, key, value)
                if item.patch.tag_ids is not None:
                    tags = (
                        self.db.query(models.Tag)
                        .filter(models.Tag.id.in_(item.patch.tag_ids))
                        .all()
                    )
                    db_task.tags = tags
                updated.append(db_task)
            self.db.commit()
            for db_task in updated:
                self.db.refresh(db_task)
            return updated
        except Exception:
            self.db.rollback()
            raise

    def batch_delete(self, ids: list[str]) -> list[str]:
        """批量刪除任務（單一交易，全成功或全回滾）

        Args:
            ids: 要刪除的任務 ID 清單

        Returns:
            list[str]: 成功刪除的 ID 清單（保持輸入順序）

        Raises:
            ValueError: 當 ids 為空
            TaskNotFound: 任一 id 在資料庫中不存在
        """
        if not ids:
            raise ValueError("ids must not be empty")

        existing_map = {
            t.id: t
            for t in self.db.query(models.Task).filter(models.Task.id.in_(ids)).all()
        }
        for task_id in ids:
            if task_id not in existing_map:
                raise TaskNotFound(task_id)

        try:
            for task_id in ids:
                self.db.delete(existing_map[task_id])
            self.db.commit()
            return list(ids)
        except Exception:
            self.db.rollback()
            raise
