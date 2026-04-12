import hmac
import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# 不需要認證的路徑前綴
_PUBLIC_PREFIXES = ("/", "/assets/")


class ApiKeyAuthMiddleware(BaseHTTPMiddleware):
    """API Key 認證中介層。

    When MOVERA_API_KEY env var is set and non-empty, all /api/ and /webhook/
    routes require a valid API key via Authorization: Bearer <key> or X-API-Key header.
    Static assets and SPA routes are excluded.
    """

    def __init__(self, app, api_key: str):
        super().__init__(app)
        self.api_key = api_key

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # 靜態資源與 SPA 路由不需認證
        if not path.startswith("/api/") and not path.startswith("/webhook/"):
            return await call_next(request)

        # 從 header 取得 API Key
        key = None
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            key = auth_header[7:]
        if not key:
            key = request.headers.get("x-api-key")

        # Timing-safe 比對，防止 timing attack
        if not key or not hmac.compare_digest(key, self.api_key):
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized"},
            )

        return await call_next(request)


def setup_api_key_auth(app: FastAPI) -> None:
    """設定 API Key 認證中介層。

    僅在 MOVERA_API_KEY 環境變數已設定且非空時啟用。
    """
    api_key = os.environ.get("MOVERA_API_KEY", "").strip()
    if api_key:
        app.add_middleware(ApiKeyAuthMiddleware, api_key=api_key)
