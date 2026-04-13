from typing import Optional

from fastapi import APIRouter, Depends, Query

from backend import schemas
from backend.dependencies import depends_preset_rule_service
from backend.services.preset_rule_service import PresetRuleService

router = APIRouter(prefix="/api/v1", tags=["Preset Rules"])


@router.get("/preset-rules", response_model=list[schemas.PresetRule_], summary="獲取所有常用規則")
def get_all_preset_rules(
    rule_type: Optional[str] = Query(None, description="篩選規則類型（parse 或 regex）"),
    field_type: Optional[str] = Query(None, description="篩選欄位類型（src 或 dst）"),
    service: PresetRuleService = Depends(depends_preset_rule_service),
):
    return service.get_all_preset_rules(rule_type=rule_type, field_type=field_type)


@router.post("/preset-rules", response_model=schemas.PresetRule_, status_code=201, summary="建立常用規則")
def create_preset_rule(
    data: schemas.PresetRuleCreate,
    service: PresetRuleService = Depends(depends_preset_rule_service),
):
    return service.create_preset_rule(data)


@router.put("/preset-rules/{preset_rule_id}", response_model=schemas.PresetRule_, summary="更新常用規則")
def update_preset_rule(
    preset_rule_id: str,
    data: schemas.PresetRuleUpdate,
    service: PresetRuleService = Depends(depends_preset_rule_service),
):
    return service.update_preset_rule(preset_rule_id, data)


@router.delete("/preset-rules/{preset_rule_id}", status_code=204, summary="刪除常用規則")
def delete_preset_rule(
    preset_rule_id: str,
    service: PresetRuleService = Depends(depends_preset_rule_service),
):
    service.delete_preset_rule(preset_rule_id)
