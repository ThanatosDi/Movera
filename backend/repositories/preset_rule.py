from typing import Optional

from sqlalchemy.orm import Session

from backend import models
from backend.schemas import PresetRuleCreate, PresetRuleUpdate


class PresetRuleRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, preset_rule_id: str) -> models.PresetRule | None:
        return self.db.query(models.PresetRule).filter(models.PresetRule.id == preset_rule_id).first()

    def get_by_name(self, name: str) -> models.PresetRule | None:
        return self.db.query(models.PresetRule).filter(models.PresetRule.name == name).first()

    def get_all(
        self,
        rule_type: Optional[str] = None,
        field_type: Optional[str] = None,
    ) -> list[models.PresetRule]:
        query = self.db.query(models.PresetRule)
        if rule_type is not None:
            query = query.filter(models.PresetRule.rule_type == rule_type)
        if field_type is not None:
            query = query.filter(models.PresetRule.field_type == field_type)
        return query.order_by(models.PresetRule.created_at.asc()).all()

    def create(self, preset_rule: PresetRuleCreate) -> models.PresetRule:
        db_rule = models.PresetRule(**preset_rule.model_dump())
        self.db.add(db_rule)
        self.db.commit()
        self.db.refresh(db_rule)
        return db_rule

    def update(self, preset_rule_id: str, preset_rule_update: PresetRuleUpdate) -> models.PresetRule | None:
        db_rule = self.get_by_id(preset_rule_id)
        if db_rule:
            update_data = preset_rule_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_rule, key, value)
            self.db.commit()
            self.db.refresh(db_rule)
        return db_rule

    def delete(self, preset_rule_id: str) -> models.PresetRule | None:
        db_rule = self.get_by_id(preset_rule_id)
        if db_rule:
            self.db.delete(db_rule)
            self.db.commit()
        return db_rule
