"""
批量 Task Schemas 單元測試
"""

import pytest
from pydantic import ValidationError

from backend import schemas


class TestTaskBatchCreate:
    def test_accepts_list_of_task_create(self):
        payload = {
            "items": [
                {"name": "A", "include": "kw", "move_to": "/a"},
                {"name": "B", "include": "kw", "move_to": "/b"},
            ]
        }
        obj = schemas.TaskBatchCreate(**payload)
        assert len(obj.items) == 2
        assert obj.items[0].name == "A"


class TestTaskBatchUpdate:
    def test_accepts_items_with_id_and_patch(self):
        payload = {
            "items": [
                {"id": "id-1", "patch": {"enabled": False}},
            ]
        }
        obj = schemas.TaskBatchUpdate(**payload)
        assert obj.items[0].id == "id-1"
        assert obj.items[0].patch.enabled is False

    def test_patch_rejects_unknown_fields(self):
        with pytest.raises(ValidationError):
            schemas.TaskPatch(unknown_field="x")

    def test_patch_all_optional(self):
        patch = schemas.TaskPatch()
        dumped = patch.model_dump(exclude_unset=True)
        assert dumped == {}


class TestTaskBatchDelete:
    def test_accepts_string_ids(self):
        obj = schemas.TaskBatchDelete(ids=["a", "b", "c"])
        assert obj.ids == ["a", "b", "c"]


class TestTaskBatchResult:
    def test_default_empty(self):
        result = schemas.TaskBatchResult()
        assert result.items == []
        assert result.deleted_ids == []
