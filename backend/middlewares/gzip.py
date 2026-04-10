from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware


def setup_gzip(app: FastAPI):
    """
    設定 FastAPI 應用程式的 GZIP (壓縮) 中介軟體。
    """
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000,
        compresslevel=5,
    )
