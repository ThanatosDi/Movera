import pytest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient


@pytest.fixture
def spa_client(tmp_path):
    """建立帶有臨時 DIST_DIR 的測試 client"""
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    # 建立測試用靜態檔案
    (dist_dir / "index.html").write_text("<html>SPA</html>")
    (dist_dir / "favicon.ico").write_bytes(b"icon")

    # 在 dist 外建立機密檔案
    secret = tmp_path / "secret.txt"
    secret.write_text("SECRET DATA")

    with patch("main.DIST_DIR", dist_dir):
        # 需要重新載入以套用 patch
        from main import app
        client = TestClient(app)
        yield client


class TestSPARoutePathTraversal:
    """SPA 路由路徑穿越防護測試"""

    def test_normal_static_file(self, spa_client):
        """正常靜態檔案路徑應回傳該檔案"""
        response = spa_client.get("/favicon.ico")
        assert response.status_code == 200
        assert response.content == b"icon"

    def test_path_traversal_returns_fallback(self, spa_client):
        """含 .. 的路徑不應回傳目標檔案，應回傳 index.html fallback"""
        response = spa_client.get("/../secret.txt")
        assert response.status_code == 200
        # 應回傳 index.html（SPA fallback），不是 secret.txt
        assert b"SECRET DATA" not in response.content
        assert b"SPA" in response.content
