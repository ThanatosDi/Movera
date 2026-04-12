from typing import Optional

from backend import models, schemas
from backend.exceptions.preset_rule_exception import (
    PresetRuleAlreadyExists,
    PresetRuleNotFound,
)
from backend.repositories.preset_rule import PresetRuleRepository


class PresetRuleService:
    def __init__(self, repository: PresetRuleRepository):
        self.repository = repository

    def _get_or_raise(self, preset_rule_id: str) -> models.PresetRule:
        rule = self.repository.get_by_id(preset_rule_id)
        if rule is None:
            raise PresetRuleNotFound(preset_rule_id)
        return rule

    def get_all_preset_rules(
        self,
        rule_type: Optional[str] = None,
        field_type: Optional[str] = None,
    ) -> list[models.PresetRule]:
        return self.repository.get_all(rule_type=rule_type, field_type=field_type)

    def create_preset_rule(self, data: schemas.PresetRuleCreate) -> models.PresetRule:
        existing = self.repository.get_by_name(data.name)
        if existing is not None:
            raise PresetRuleAlreadyExists(data.name)
        return self.repository.create(data)

    def update_preset_rule(self, preset_rule_id: str, data: schemas.PresetRuleUpdate) -> models.PresetRule:
        existing = self._get_or_raise(preset_rule_id)
        if existing.name != data.name:
            same_name = self.repository.get_by_name(data.name)
            if same_name is not None:
                raise PresetRuleAlreadyExists(data.name)
        return self.repository.update(preset_rule_id, data)

    def delete_preset_rule(self, preset_rule_id: str) -> models.PresetRule:
        self._get_or_raise(preset_rule_id)
        return self.repository.delete(preset_rule_id)
