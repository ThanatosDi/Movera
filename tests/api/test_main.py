import httpx
import pytest
from fastapi.testclient import TestClient

from api.main import app

# 關閉 lifespan，避免測試啟動時執行資料庫遷移
client = TestClient(app)


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}


def test_serve_vue_catch_all_for_frontend_route(mocker):
    """測試 catch-all 路由是否為前端路由回傳 index.html"""
    mock_file_response = mocker.patch("api.main.FileResponse")
    # 模擬 os.path.join 以回傳預期的路徑
    mocker.patch("os.path.join", return_value="dist/index.html")

    response = client.get("/some/frontend/route")
    # 斷言 FileResponse 被以正確的路徑呼叫
    mock_file_response.assert_called_once_with("dist/index.html")


def test_serve_vue_for_static_files(mocker):
    """測試 catch-all 路由是否正確處理靜態檔案"""
    mock_file_response = mocker.patch("api.main.FileResponse")
    mocker.patch("os.path.join", return_value="dist/favicon.ico")

    response = client.get("/favicon.ico")
    mock_file_response.assert_called_once_with("dist/favicon.ico")


def test_serve_vue_ignores_api_paths():
    """測試 catch-all 路由是否忽略 /api/ 開頭的路徑"""
    response = client.get("/api/should/be/ignored")
    # 這個請求應該被 FastAPI 的 404 處理，而不是 serve_vue
    # TestClient 會跟隨到 serve_vue，但 serve_vue 會回傳一個 dict
    assert response.json() == {"detail": "Not Found"}


@pytest.mark.asyncio
async def test_lifespan_run_migrations_failure(mocker):
    """測試 lifespan 中 run_migrations 失敗的情境"""
    # 模擬 alembic command.upgrade 拋出例外
    mocker.patch("alembic.command.upgrade", side_effect=Exception("Migration failed"))
    mock_logger_info = mocker.patch("api.main.logger.info")

    # 直接呼叫 lifespan 並捕捉例外
    with pytest.raises(Exception, match="Migration failed"):
        # 我們需要一個 dummy app 物件
        async with app.router.lifespan_context(app):
            pass

    # 驗證 logger.info 被呼叫了兩次 (開始和失敗)
    assert mock_logger_info.call_count == 2
    mock_logger_info.assert_any_call("開始資料庫遷移...")
    mock_logger_info.assert_any_call("遷移失敗: Migration failed")
