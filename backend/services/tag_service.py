from backend import models, schemas
from backend.exceptions.tag_exception import (
    InvalidTagColor,
    TagAlreadyExists,
    TagNotFound,
)
from backend.repositories.tag import TagRepository


class TagService:
    def __init__(self, repository: TagRepository):
        self.repository = repository

    def _get_tag_or_raise(self, tag_id: str) -> models.Tag:
        tag = self.repository.get_by_id(tag_id)
        if tag is None:
            raise TagNotFound(tag_id)
        return tag

    def _validate_color(self, color: str) -> None:
        if color not in schemas.ALLOWED_TAG_COLORS:
            raise InvalidTagColor(color)

    def get_all_tags(self) -> list[models.Tag]:
        return self.repository.get_all()

    def get_tag_by_id(self, tag_id: str) -> models.Tag | None:
        return self.repository.get_by_id(tag_id)

    def create_tag(self, tag: schemas.TagCreate) -> models.Tag:
        self._validate_color(tag.color)
        existing = self.repository.get_by_name(tag.name)
        if existing is not None:
            raise TagAlreadyExists(tag.name)
        return self.repository.create(tag)

    def update_tag(self, tag_id: str, tag_update: schemas.TagUpdate) -> models.Tag:
        self._validate_color(tag_update.color)
        existing = self._get_tag_or_raise(tag_id)
        if existing.name != tag_update.name:
            same_name = self.repository.get_by_name(tag_update.name)
            if same_name is not None:
                raise TagAlreadyExists(tag_update.name)
        return self.repository.update(tag_id, tag_update)

    def delete_tag(self, tag_id: str) -> models.Tag:
        self._get_tag_or_raise(tag_id)
        return self.repository.delete(tag_id)
