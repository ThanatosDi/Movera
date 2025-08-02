import os
import sys
from pathlib import Path

from loguru import logger
from loki_logger_handler.formatters.loguru_formatter import LoguruFormatter
from loki_logger_handler.loki_logger_handler import LokiLoggerHandler


def loki_handler() -> LokiLoggerHandler | None:
    if os.getenv("LOKI_URL", "") == "":
        return None
    handler = LokiLoggerHandler(
        url=os.getenv("LOKI_URL", ""),
        labels={"application": "SimilarityComparison"},
        label_keys={},
        timeout=10,
        default_formatter=LoguruFormatter(),
        additional_headers={"X-Scope-OrgID": "symmetry"},
    )
    return handler


handlers = [
    {
        "sink": sys.stdout,
        "level": os.getenv("LOG_LEVEL", "info").upper(),
        "colorize": True,
    },
    {
        "sink": "storages/logs/API_{time:YYYY-MM-DD}.log",
        "level": os.getenv("LOG_LEVEL", "info").upper(),
        "format": "{time} | {level: <8} | {name}:{function}:{line} - {message} | {extra}",
        "rotation": "00:00",
        "enqueue": True,
        "colorize": True,
    },
]

loki_logger_handler = loki_handler()
if loki_logger_handler is not None:
    handlers.append(
        {
            "sink": loki_logger_handler,
            "serialize": True,
            "level": os.getenv("LOG_LEVEL", "info").upper(),
        }
    )

logger.configure(handlers=handlers)
