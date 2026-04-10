"""
Tag Router 單元測試
"""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from backend.routers.tag import router
from backend.models.tag import Tag
from backend.services.tag_service import TagService
from backend.exceptions.tag_exception import TagAlreadyExists, TagNotFound, InvalidTagColor


@pytest.fixture
def mock_tag_service():
    """建立 mock 的 TagService"""
    return MagicMock(spec=TagService)


@pytest.fixture
def app(mock_tag_service):
    """建立測試用的 FastAPI app"""
    from backend.dependencies import depends_tag_service

    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[depends_tag_service] = lambda: mock_tag_service

    @app.exception_handler(TagNotFound)
    async def _tag_not_found(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(TagAlreadyExists)
    async def _tag_already_exists(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(InvalidTagColor)
    async def _invalid_color(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    return app


@pytest.fixture
def client(app):
    """建立測試用的 TestClient"""
    return TestClient(app, raise_server_exceptions=False)


def _make_tag(id="tag-1", name="動畫", color="blue"):
    tag = Tag()
    tag.id = id
    tag.name = name
    tag.color = color
    return tag


class TestGetAllTags:
    def test_get_all_tags_success(self, client, mock_tag_service):
        mock_tag_service.get_all_tags.return_value = [
            _make_tag(id="1", name="動畫", color="blue"),
            _make_tag(id="2", name="電影", color="red"),
        ]
        response = client.get("/api/v1/tags")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "動畫"


class TestCreateTag:
    def test_create_tag_success(self, client, mock_tag_service):
        mock_tag_service.create_tag.return_value = _make_tag()
        response = client.post("/api/v1/tags", json={"name": "動畫", "color": "blue"})
        assert response.status_code == 201
        assert response.json()["name"] == "動畫"

    def test_create_tag_duplicate_name_409(self, client, mock_tag_service):
        mock_tag_service.create_tag.side_effect = TagAlreadyExists("動畫")
        response = client.post("/api/v1/tags", json={"name": "動畫", "color": "blue"})
        assert response.status_code == 409

    def test_create_tag_invalid_color_422(self, client, mock_tag_service):
        mock_tag_service.create_tag.side_effect = InvalidTagColor("neon")
        response = client.post("/api/v1/tags", json={"name": "測試", "color": "neon"})
        assert response.status_code == 422


class TestUpdateTag:
    def test_update_tag_success(self, client, mock_tag_service):
        mock_tag_service.update_tag.return_value = _make_tag(name="新名稱", color="red")
        response = client.put("/api/v1/tags/tag-1", json={"name": "新名稱", "color": "red"})
        assert response.status_code == 200
        assert response.json()["name"] == "新名稱"

    def test_update_tag_not_found(self, client, mock_tag_service):
        mock_tag_service.update_tag.side_effect = TagNotFound("non-existent")
        response = client.put("/api/v1/tags/non-existent", json={"name": "名稱", "color": "blue"})
        assert response.status_code == 404


class TestDeleteTag:
    def test_delete_tag_success(self, client, mock_tag_service):
        mock_tag_service.delete_tag.return_value = _make_tag()
        response = client.delete("/api/v1/tags/tag-1")
        assert response.status_code == 204

    def test_delete_tag_not_found(self, client, mock_tag_service):
        mock_tag_service.delete_tag.side_effect = TagNotFound("non-existent")
        response = client.delete("/api/v1/tags/non-existent")
        assert response.status_code == 404
