from fastapi import FastAPI, Response
from fastapi.testclient import TestClient

from api.middlewares.gzip import setup_gzip


def test_gzip_middleware_small_response():
    """
    測試當回應小於 minimum_size 時，GzipMiddleware 不會壓縮回應。
    """
    app = FastAPI()
    setup_gzip(app)

    @app.get("/")
    def read_main():
        return Response("a" * 999)

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "Content-Encoding" not in response.headers
    assert len(response.content) == 999


def test_gzip_middleware_large_response():
    """
    測試當回應大於 minimum_size 時，GzipMiddleware 會壓縮回應。
    """
    app = FastAPI()
    setup_gzip(app)

    @app.get("/")
    def read_main():
        return Response("a" * 1001)

    client = TestClient(app)
    # 需在 header 中加入 "Accept-Encoding": "gzip" 才會觸發壓縮
    response = client.get("/", headers={"Accept-Encoding": "gzip"})
    assert response.status_code == 200
    assert response.headers["Content-Encoding"] == "gzip"
    # 驗證壓縮後的內容長度小於原始長度
    assert "content-length" in response.headers
    assert int(response.headers["content-length"]) < 1001
