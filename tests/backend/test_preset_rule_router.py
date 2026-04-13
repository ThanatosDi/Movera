"""
PresetRule Router 單元測試
"""

from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.exceptions.preset_rule_exception import (
    PresetRuleAlreadyExists,
    PresetRuleNotFound,
)
from backend.models.preset_rule import PresetRule
from backend.routers.preset_rule import router
from backend.services.preset_rule_service import PresetRuleService


@pytest.fixture
def mock_service():
    return MagicMock(spec=PresetRuleService)


@pytest.fixture
def app(mock_service):
    from backend.dependencies import depends_preset_rule_service

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[depends_preset_rule_service] = lambda: mock_service

    @app.exception_handler(PresetRuleNotFound)
    async def _not_found(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(PresetRuleAlreadyExists)
    async def _already_exists(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    return app


@pytest.fixture
def client(app):
    return TestClient(app, raise_server_exceptions=False)


def _make_rule(id="rule-1", name="動畫季番命名", rule_type="parse", field_type="src", pattern="{title} - {ep}.mp4"):
    from datetime import UTC, datetime
    rule = PresetRule()
    rule.id = id
    rule.name = name
    rule.rule_type = rule_type
    rule.field_type = field_type
    rule.pattern = pattern
    rule.created_at = datetime.now(UTC)
    return rule


class TestGetAllPresetRules:
    def test_get_all_success(self, client, mock_service):
        mock_service.get_all_preset_rules.return_value = [
            _make_rule(id="1"),
            _make_rule(id="2", name="電影字幕", rule_type="regex", field_type="dst"),
        ]
        response = client.get("/api/v1/preset-rules")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_filter_by_rule_type(self, client, mock_service):
        mock_service.get_all_preset_rules.return_value = [_make_rule()]
        response = client.get("/api/v1/preset-rules?rule_type=parse")
        assert response.status_code == 200
        mock_service.get_all_preset_rules.assert_called_with(rule_type="parse", field_type=None)

    def test_filter_by_field_type(self, client, mock_service):
        mock_service.get_all_preset_rules.return_value = []
        response = client.get("/api/v1/preset-rules?field_type=src")
        assert response.status_code == 200
        mock_service.get_all_preset_rules.assert_called_with(rule_type=None, field_type="src")


class TestCreatePresetRule:
    def test_create_success(self, client, mock_service):
        mock_service.create_preset_rule.return_value = _make_rule()
        response = client.post("/api/v1/preset-rules", json={
            "name": "動畫季番命名", "rule_type": "parse", "field_type": "src", "pattern": "{title} - {ep}.mp4",
        })
        assert response.status_code == 201
        assert response.json()["name"] == "動畫季番命名"

    def test_create_duplicate_409(self, client, mock_service):
        mock_service.create_preset_rule.side_effect = PresetRuleAlreadyExists("動畫季番命名")
        response = client.post("/api/v1/preset-rules", json={
            "name": "動畫季番命名", "rule_type": "parse", "field_type": "src", "pattern": "p",
        })
        assert response.status_code == 409


class TestUpdatePresetRule:
    def test_update_success(self, client, mock_service):
        mock_service.update_preset_rule.return_value = _make_rule(name="新名稱")
        response = client.put("/api/v1/preset-rules/rule-1", json={
            "name": "新名稱", "rule_type": "parse", "field_type": "src", "pattern": "p",
        })
        assert response.status_code == 200
        assert response.json()["name"] == "新名稱"

    def test_update_not_found(self, client, mock_service):
        mock_service.update_preset_rule.side_effect = PresetRuleNotFound("non-existent")
        response = client.put("/api/v1/preset-rules/non-existent", json={
            "name": "x", "rule_type": "parse", "field_type": "src", "pattern": "p",
        })
        assert response.status_code == 404


class TestDeletePresetRule:
    def test_delete_success(self, client, mock_service):
        mock_service.delete_preset_rule.return_value = _make_rule()
        response = client.delete("/api/v1/preset-rules/rule-1")
        assert response.status_code == 204

    def test_delete_not_found(self, client, mock_service):
        mock_service.delete_preset_rule.side_effect = PresetRuleNotFound("non-existent")
        response = client.delete("/api/v1/preset-rules/non-existent")
        assert response.status_code == 404
