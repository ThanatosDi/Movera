"""
PresetRuleService 單元測試
"""

import pytest

from backend.exceptions.preset_rule_exception import (
    PresetRuleAlreadyExists,
    PresetRuleNotFound,
)
from backend.schemas import PresetRuleCreate, PresetRuleUpdate


class TestPresetRuleServiceCreate:
    def test_create_success(self, preset_rule_service, sample_preset_rule_data):
        rule = preset_rule_service.create_preset_rule(PresetRuleCreate(**sample_preset_rule_data))
        assert rule.name == sample_preset_rule_data["name"]

    def test_create_duplicate_name(self, preset_rule_service, sample_preset_rule_data):
        preset_rule_service.create_preset_rule(PresetRuleCreate(**sample_preset_rule_data))
        with pytest.raises(PresetRuleAlreadyExists):
            preset_rule_service.create_preset_rule(PresetRuleCreate(**sample_preset_rule_data))


class TestPresetRuleServiceGetAll:
    def test_get_all(self, preset_rule_service, sample_preset_rule_data, sample_preset_rule_data_2):
        preset_rule_service.create_preset_rule(PresetRuleCreate(**sample_preset_rule_data))
        preset_rule_service.create_preset_rule(PresetRuleCreate(**sample_preset_rule_data_2))
        rules = preset_rule_service.get_all_preset_rules()
        assert len(rules) == 2

    def test_get_all_with_filter(self, preset_rule_service, sample_preset_rule_data, sample_preset_rule_data_2):
        preset_rule_service.create_preset_rule(PresetRuleCreate(**sample_preset_rule_data))
        preset_rule_service.create_preset_rule(PresetRuleCreate(**sample_preset_rule_data_2))
        rules = preset_rule_service.get_all_preset_rules(rule_type="parse")
        assert len(rules) == 1


class TestPresetRuleServiceUpdate:
    def test_update_success(self, preset_rule_service, sample_preset_rule_data):
        created = preset_rule_service.create_preset_rule(PresetRuleCreate(**sample_preset_rule_data))
        updated = preset_rule_service.update_preset_rule(
            created.id,
            PresetRuleUpdate(name="新規則", rule_type="regex", field_type="dst", pattern="new"),
        )
        assert updated.name == "新規則"

    def test_update_not_found(self, preset_rule_service):
        with pytest.raises(PresetRuleNotFound):
            preset_rule_service.update_preset_rule(
                "non-existent",
                PresetRuleUpdate(name="x", rule_type="parse", field_type="src", pattern="p"),
            )

    def test_update_duplicate_name(self, preset_rule_service, sample_preset_rule_data, sample_preset_rule_data_2):
        preset_rule_service.create_preset_rule(PresetRuleCreate(**sample_preset_rule_data))
        created2 = preset_rule_service.create_preset_rule(PresetRuleCreate(**sample_preset_rule_data_2))
        with pytest.raises(PresetRuleAlreadyExists):
            preset_rule_service.update_preset_rule(
                created2.id,
                PresetRuleUpdate(
                    name=sample_preset_rule_data["name"],
                    rule_type="regex",
                    field_type="dst",
                    pattern="p",
                ),
            )


class TestPresetRuleServiceDelete:
    def test_delete_success(self, preset_rule_service, sample_preset_rule_data):
        created = preset_rule_service.create_preset_rule(PresetRuleCreate(**sample_preset_rule_data))
        preset_rule_service.delete_preset_rule(created.id)
        rules = preset_rule_service.get_all_preset_rules()
        assert len(rules) == 0

    def test_delete_not_found(self, preset_rule_service):
        with pytest.raises(PresetRuleNotFound):
            preset_rule_service.delete_preset_rule("non-existent")
