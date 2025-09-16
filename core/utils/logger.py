import os
import sys
from pathlib import Path

from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOG_DIR = PROJECT_ROOT.joinpath("storages", "logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger.remove(0)  # Remove default handler

logger.add(
    sys.stderr,
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    colorize=True,
)
logger.add(
    LOG_DIR.as_posix() + "/API_{time:YYYY-MM-DD}.log",
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="{time:YYYY-MM-DDTHH:mm:ss.SSSSZ} | {level: <8} | {name}:{function}:{line} - {message} | {extra}",
    rotation="00:00",  # Rotate daily at midnight
    enqueue=True,
    encoding="utf-8",
    colorize=True,
    retention=3,
)
logger.add(
    LOG_DIR.as_posix() + "/APP_{time:YYYY-MM-DD}.log",
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="{time:YYYY-MM-DDTHH:mm:ss.SSSSZ} | {level: <8} | {name}:{function}:{line} - {message} | {extra}",
    rotation="00:00",  # Rotate daily at midnight
    enqueue=True,
    encoding="utf-8",
    colorize=True,
    filter=lambda record: record["extra"].get("app", None) == "app",
    retention=3,
)
