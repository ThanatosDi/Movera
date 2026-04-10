from sqlalchemy.orm import Session

from backend import models
from backend.schemas import TagCreate, TagUpdate


class TagRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, tag_id: str) -> models.Tag | None:
        return self.db.query(models.Tag).filter(models.Tag.id == tag_id).first()

    def get_by_name(self, name: str) -> models.Tag | None:
        return self.db.query(models.Tag).filter(models.Tag.name == name).first()

    def get_all(self) -> list[models.Tag]:
        return self.db.query(models.Tag).all()

    def create(self, tag: TagCreate) -> models.Tag:
        db_tag = models.Tag(**tag.model_dump())
        self.db.add(db_tag)
        self.db.commit()
        self.db.refresh(db_tag)
        return db_tag

    def update(self, tag_id: str, tag_update: TagUpdate) -> models.Tag | None:
        db_tag = self.get_by_id(tag_id)
        if db_tag:
            update_data = tag_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_tag, key, value)
            self.db.commit()
            self.db.refresh(db_tag)
        return db_tag

    def delete(self, tag_id: str) -> models.Tag | None:
        db_tag = self.get_by_id(tag_id)
        if db_tag:
            self.db.delete(db_tag)
            self.db.commit()
        return db_tag
