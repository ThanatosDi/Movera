"""
TagRepository 單元測試
"""

import pytest

from backend.schemas import TagCreate, TagUpdate


class TestTagRepositoryCreate:
    def test_create_tag_success(self, tag_repository, sample_tag_data):
        tag = tag_repository.create(TagCreate(**sample_tag_data))
        assert tag is not None
        assert tag.name == sample_tag_data["name"]
        assert tag.color == sample_tag_data["color"]
        assert tag.id is not None

    def test_create_tag_duplicate_name(self, tag_repository, sample_tag_data):
        tag_repository.create(TagCreate(**sample_tag_data))
        with pytest.raises(Exception):
            tag_repository.create(TagCreate(**sample_tag_data))


class TestTagRepositoryGetAll:
    def test_get_all_empty(self, tag_repository):
        tags = tag_repository.get_all()
        assert tags == []

    def test_get_all_with_tags(self, tag_repository, sample_tag_data, sample_tag_data_2):
        tag_repository.create(TagCreate(**sample_tag_data))
        tag_repository.create(TagCreate(**sample_tag_data_2))
        tags = tag_repository.get_all()
        assert len(tags) == 2


class TestTagRepositoryGetById:
    def test_get_by_id_success(self, tag_repository, sample_tag_data):
        created = tag_repository.create(TagCreate(**sample_tag_data))
        found = tag_repository.get_by_id(created.id)
        assert found is not None
        assert found.id == created.id

    def test_get_by_id_not_found(self, tag_repository):
        found = tag_repository.get_by_id("non-existent-id")
        assert found is None


class TestTagRepositoryUpdate:
    def test_update_tag_success(self, tag_repository, sample_tag_data):
        created = tag_repository.create(TagCreate(**sample_tag_data))
        updated = tag_repository.update(created.id, TagUpdate(name="新名稱", color="red"))
        assert updated is not None
        assert updated.name == "新名稱"
        assert updated.color == "red"

    def test_update_tag_not_found(self, tag_repository):
        result = tag_repository.update("non-existent-id", TagUpdate(name="名稱", color="blue"))
        assert result is None


class TestTagRepositoryDelete:
    def test_delete_tag_success(self, tag_repository, sample_tag_data):
        created = tag_repository.create(TagCreate(**sample_tag_data))
        deleted = tag_repository.delete(created.id)
        assert deleted is not None
        assert deleted.id == created.id
        assert tag_repository.get_by_id(created.id) is None

    def test_delete_tag_not_found(self, tag_repository):
        result = tag_repository.delete("non-existent-id")
        assert result is None
