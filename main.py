from pathlib import Path

import uvicorn
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.backend import app

# 靜態檔案目錄路徑
DIST_DIR = Path(__file__).parent / "dist"


def setup_static_files():
    """設定 Vue 應用的靜態檔案服務"""

    # 掛載靜態資源目錄
    if (DIST_DIR / "assets").exists():
        app.mount("/assets", StaticFiles(directory=DIST_DIR / "assets"), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_index():
        """提供 Vue 應用的入口頁面"""
        return FileResponse(DIST_DIR / "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """處理 SPA 路由，將未匹配的路徑導向 index.html"""
        # 嘗試提供靜態檔案
        file_path = DIST_DIR / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        # 返回 index.html 讓 Vue Router 處理路由
        return FileResponse(DIST_DIR / "index.html")


if __name__ == "__main__":
    setup_static_files()
    for route in app.routes:
        print(route)

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
