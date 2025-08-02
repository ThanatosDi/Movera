from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from api.models.database import Tag


class TagRepository:
    def get_all(self, session: Session):
        return session.scalars(select(Tag)).all()

    def get(self, session: Session, tag_id: int):
        task = session.scalars(select(Tag).where(Tag.id == tag_id)).one_or_none()
        return task

    def create(self, session: Session, tag: Tag):
        session.add(tag)
        session.commit()

    def update(self, session: Session, tag_id: int, tag: Tag):
        exist_tag = session.scalars(
            select(Tag).where(Tag.id == tag_id)
        ).one_or_none()
        if exist_tag is None:
            raise NoResultFound(f"Tag {tag_id} not found")

        exist_tag.name = tag.name
        exist_tag.color = tag.color
        session.add(exist_tag)
        session.commit()

    def delete(self, session: Session, tag_id: int):
        tag = session.scalars(select(Tag).where(Tag.id == tag_id)).one()
        if tag:
            session.delete(tag)
            session.commit()
