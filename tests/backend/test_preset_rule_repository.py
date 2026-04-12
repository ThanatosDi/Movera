"""
PresetRuleRepository 單元測試
"""

import pytest

from backend.schemas import PresetRuleCreate, PresetRuleUpdate


class TestPresetRuleRepositoryCreate:
    def test_create_success(self, preset_rule_repository, sample_preset_rule_data):
        rule = preset_rule_repository.create(PresetRuleCreate(**sample_preset_rule_data))
        assert rule is not None
        assert rule.name == sample_preset_rule_data["name"]
        assert rule.rule_type == sample_preset_rule_data["rule_type"]
        assert rule.field_type == sample_preset_rule_data["field_type"]
        assert rule.pattern == sample_preset_rule_data["pattern"]
        assert rule.id is not None

    def test_create_duplicate_name(self, preset_rule_repository, sample_preset_rule_data):
        preset_rule_repository.create(PresetRuleCreate(**sample_preset_rule_data))
        with pytest.raises(Exception):
            preset_rule_repository.create(PresetRuleCreate(**sample_preset_rule_data))


class TestPresetRuleRepositoryGetAll:
    def test_get_all_empty(self, preset_rule_repository):
        rules = preset_rule_repository.get_all()
        assert rules == []

    def test_get_all_with_rules(self, preset_rule_repository, sample_preset_rule_data, sample_preset_rule_data_2):
        preset_rule_repository.create(PresetRuleCreate(**sample_preset_rule_data))
        preset_rule_repository.create(PresetRuleCreate(**sample_preset_rule_data_2))
        rules = preset_rule_repository.get_all()
        assert len(rules) == 2

    def test_filter_by_rule_type(self, preset_rule_repository, sample_preset_rule_data, sample_preset_rule_data_2):
        preset_rule_repository.create(PresetRuleCreate(**sample_preset_rule_data))
        preset_rule_repository.create(PresetRuleCreate(**sample_preset_rule_data_2))
        rules = preset_rule_repository.get_all(rule_type="parse")
        assert len(rules) == 1
        assert rules[0].rule_type == "parse"

    def test_filter_by_field_type(self, preset_rule_repository, sample_preset_rule_data, sample_preset_rule_data_2):
        preset_rule_repository.create(PresetRuleCreate(**sample_preset_rule_data))
        preset_rule_repository.create(PresetRuleCreate(**sample_preset_rule_data_2))
        rules = preset_rule_repository.get_all(field_type="dst")
        assert len(rules) == 1
        assert rules[0].field_type == "dst"

    def test_filter_by_both(self, preset_rule_repository, sample_preset_rule_data, sample_preset_rule_data_2):
        preset_rule_repository.create(PresetRuleCreate(**sample_preset_rule_data))
        preset_rule_repository.create(PresetRuleCreate(**sample_preset_rule_data_2))
        rules = preset_rule_repository.get_all(rule_type="regex", field_type="dst")
        assert len(rules) == 1
        assert rules[0].name == sample_preset_rule_data_2["name"]


class TestPresetRuleRepositoryGetById:
    def test_get_by_id_success(self, preset_rule_repository, sample_preset_rule_data):
        created = preset_rule_repository.create(PresetRuleCreate(**sample_preset_rule_data))
        found = preset_rule_repository.get_by_id(created.id)
        assert found is not None
        assert found.id == created.id

    def test_get_by_id_not_found(self, preset_rule_repository):
        found = preset_rule_repository.get_by_id("non-existent-id")
        assert found is None


class TestPresetRuleRepositoryUpdate:
    def test_update_success(self, preset_rule_repository, sample_preset_rule_data):
        created = preset_rule_repository.create(PresetRuleCreate(**sample_preset_rule_data))
        updated = preset_rule_repository.update(
            created.id,
            PresetRuleUpdate(name="新名稱", rule_type="regex", field_type="dst", pattern="new pattern"),
        )
        assert updated is not None
        assert updated.name == "新名稱"
        assert updated.rule_type == "regex"

    def test_update_not_found(self, preset_rule_repository):
        result = preset_rule_repository.update(
            "non-existent-id",
            PresetRuleUpdate(name="名稱", rule_type="parse", field_type="src", pattern="p"),
        )
        assert result is None


class TestPresetRuleRepositoryDelete:
    def test_delete_success(self, preset_rule_repository, sample_preset_rule_data):
        created = preset_rule_repository.create(PresetRuleCreate(**sample_preset_rule_data))
        deleted = preset_rule_repository.delete(created.id)
        assert deleted is not None
        assert preset_rule_repository.get_by_id(created.id) is None

    def test_delete_not_found(self, preset_rule_repository):
        result = preset_rule_repository.delete("non-existent-id")
        assert result is None
