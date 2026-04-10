"""
Task-Tag 關聯功能測試
"""

import pytest

from backend.schemas import TagCreate, TaskCreate, TaskUpdate


class TestTaskTagCreate:
    def test_create_task_with_tag_ids(self, task_repository, tag_repository, sample_task_data, sample_tag_data):
        tag = tag_repository.create(TagCreate(**sample_tag_data))
        task_data = {**sample_task_data, "tag_ids": [tag.id]}
        task = task_repository.create(TaskCreate(**task_data))
        assert len(task.tags) == 1
        assert task.tags[0].id == tag.id

    def test_create_task_with_multiple_tag_ids(self, task_repository, tag_repository, sample_task_data, sample_tag_data, sample_tag_data_2):
        tag1 = tag_repository.create(TagCreate(**sample_tag_data))
        tag2 = tag_repository.create(TagCreate(**sample_tag_data_2))
        task_data = {**sample_task_data, "tag_ids": [tag1.id, tag2.id]}
        task = task_repository.create(TaskCreate(**task_data))
        assert len(task.tags) == 2

    def test_create_task_without_tag_ids(self, task_repository, sample_task_data):
        task = task_repository.create(TaskCreate(**sample_task_data))
        assert task.tags == []


class TestTaskTagUpdate:
    def test_update_task_tags_replaced(self, task_repository, tag_repository, sample_task_data, sample_tag_data, sample_tag_data_2):
        tag1 = tag_repository.create(TagCreate(**sample_tag_data))
        tag2 = tag_repository.create(TagCreate(**sample_tag_data_2))
        task_data = {**sample_task_data, "tag_ids": [tag1.id]}
        task = task_repository.create(TaskCreate(**task_data))
        assert len(task.tags) == 1

        update_data = TaskUpdate(**{**sample_task_data, "tag_ids": [tag2.id]})
        updated = task_repository.update(task.id, update_data)
        assert len(updated.tags) == 1
        assert updated.tags[0].id == tag2.id


class TestTaskTagRead:
    def test_get_task_includes_tags(self, task_repository, tag_repository, sample_task_data, sample_tag_data):
        tag = tag_repository.create(TagCreate(**sample_tag_data))
        task_data = {**sample_task_data, "tag_ids": [tag.id]}
        created = task_repository.create(TaskCreate(**task_data))

        found = task_repository.get_by_id(created.id)
        assert len(found.tags) == 1
        assert found.tags[0].name == sample_tag_data["name"]

    def test_get_all_tasks_includes_tags(self, task_repository, tag_repository, sample_task_data, sample_tag_data):
        tag = tag_repository.create(TagCreate(**sample_tag_data))
        task_data = {**sample_task_data, "tag_ids": [tag.id]}
        task_repository.create(TaskCreate(**task_data))

        tasks = task_repository.get_all()
        assert len(tasks) == 1
        assert len(tasks[0].tags) == 1


class TestTaskTagCascadeDelete:
    def test_delete_task_clears_association(self, task_repository, tag_repository, db_session, sample_task_data, sample_tag_data):
        tag = tag_repository.create(TagCreate(**sample_tag_data))
        task_data = {**sample_task_data, "tag_ids": [tag.id]}
        task = task_repository.create(TaskCreate(**task_data))

        task_repository.delete(task.id)
        # Tag should still exist
        assert tag_repository.get_by_id(tag.id) is not None

    def test_delete_tag_clears_association(self, task_repository, tag_repository, db_session, sample_task_data, sample_tag_data):
        tag = tag_repository.create(TagCreate(**sample_tag_data))
        task_data = {**sample_task_data, "tag_ids": [tag.id]}
        task = task_repository.create(TaskCreate(**task_data))

        tag_repository.delete(tag.id)
        db_session.expire_all()
        refreshed_task = task_repository.get_by_id(task.id)
        assert refreshed_task is not None
        assert len(refreshed_task.tags) == 0
