"""
TagService 單元測試
"""

import pytest

from backend.schemas import TagCreate, TagUpdate
from backend.exceptions.tag_exception import TagAlreadyExists, TagNotFound, InvalidTagColor


class TestTagServiceCreateTag:
    def test_create_tag_success(self, tag_service, sample_tag_data):
        tag = tag_service.create_tag(TagCreate(**sample_tag_data))
        assert tag is not None
        assert tag.name == sample_tag_data["name"]
        assert tag.color == sample_tag_data["color"]

    def test_create_tag_duplicate_name(self, tag_service, sample_tag_data):
        tag_service.create_tag(TagCreate(**sample_tag_data))
        with pytest.raises(TagAlreadyExists):
            tag_service.create_tag(TagCreate(**sample_tag_data))

    def test_create_tag_invalid_color(self, tag_service):
        with pytest.raises(InvalidTagColor):
            tag_service.create_tag(TagCreate(name="測試", color="neon"))


class TestTagServiceGetAllTags:
    def test_get_all_tags_empty(self, tag_service):
        tags = tag_service.get_all_tags()
        assert tags == []

    def test_get_all_tags_with_tags(self, tag_service, sample_tag_data, sample_tag_data_2):
        tag_service.create_tag(TagCreate(**sample_tag_data))
        tag_service.create_tag(TagCreate(**sample_tag_data_2))
        tags = tag_service.get_all_tags()
        assert len(tags) == 2


class TestTagServiceUpdateTag:
    def test_update_tag_success(self, tag_service, sample_tag_data):
        created = tag_service.create_tag(TagCreate(**sample_tag_data))
        updated = tag_service.update_tag(created.id, TagUpdate(name="新名稱", color="green"))
        assert updated.name == "新名稱"
        assert updated.color == "green"

    def test_update_tag_not_found(self, tag_service):
        with pytest.raises(TagNotFound):
            tag_service.update_tag("non-existent-id", TagUpdate(name="名稱", color="blue"))

    def test_update_tag_invalid_color(self, tag_service, sample_tag_data):
        created = tag_service.create_tag(TagCreate(**sample_tag_data))
        with pytest.raises(InvalidTagColor):
            tag_service.update_tag(created.id, TagUpdate(name="名稱", color="neon"))

    def test_update_tag_duplicate_name(self, tag_service, sample_tag_data, sample_tag_data_2):
        tag_service.create_tag(TagCreate(**sample_tag_data))
        tag2 = tag_service.create_tag(TagCreate(**sample_tag_data_2))
        with pytest.raises(TagAlreadyExists):
            tag_service.update_tag(tag2.id, TagUpdate(name=sample_tag_data["name"], color="red"))


class TestTagServiceDeleteTag:
    def test_delete_tag_success(self, tag_service, sample_tag_data):
        created = tag_service.create_tag(TagCreate(**sample_tag_data))
        deleted = tag_service.delete_tag(created.id)
        assert deleted.id == created.id

    def test_delete_tag_not_found(self, tag_service):
        with pytest.raises(TagNotFound):
            tag_service.delete_tag("non-existent-id")
