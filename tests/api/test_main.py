from fastapi.testclient import TestClient

from api.main import app

# 關閉 lifespan，避免測試啟動時執行資料庫遷移
client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Movera API"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}
