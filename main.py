import os
import sys
import threading
import time
from pathlib import Path
from queue import Queue

from loguru import logger
from watchdog.observers.polling import PollingObserver

from app.event import FileMonitorHandler
from app.utils import read_config
from app.worker import Worker

MOVERA_CONFIG = os.getenv("MOVERA_CONFIG", "./config/movera.yaml")

if not Path(MOVERA_CONFIG).exists():
    raise FileNotFoundError("請設定 MOVERA_CONFIG 環境變數")


def main():
    config = read_config(MOVERA_CONFIG)
    queue = Queue()
    worker = Worker(queue)
    observer = PollingObserver()
    event_handler = FileMonitorHandler(queue)

    handlers = [
        {"sink": sys.stdout, "level": config.log.level, "colorize": True},
        {
            "sink": "./storages/logs/app_{time:YYYY-MM-DD}.log",
            "level": config.log.level,
            "format": "{time} | {level: <8} | {name}:{function}:{line} - {message} | {extra}",
            "rotation": "00:00",
            "enqueue": True,
            "colorize": True,
        },
    ]

    logger.configure(handlers=handlers)

    t = threading.Thread(target=worker.file_processing_worker, daemon=True)
    t.start()

    monitor = threading.Thread(target=worker.monitor_thread, args=(observer,), daemon=True)
    monitor.start()

    for watch_dir in config.watches:
        observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()
    logger.info(f"開始監控資料夾: {config.watches}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    t.join()
    monitor.join()
    observer.join()


if __name__ == "__main__":
    main()
