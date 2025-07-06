import os
import threading
import time
from pathlib import Path
from queue import Queue

from loguru import logger
from watchdog.observers.polling import PollingObserver

from app.event import FileEventHandler
from app.utils import read_config

MOVERA_CONFIG = os.getenv("MOVERA_CONFIG", "./config/movera.yaml")

if not Path(MOVERA_CONFIG).exists():
    raise FileNotFoundError("請設定 MOVERA_CONFIG 環境變數")

config = read_config(MOVERA_CONFIG)
queue = Queue()


def file_processing_worker(queue: Queue):
    from app.utils import job

    while True:
        src_path = queue.get()
        logger.info(f"處理檔案: {src_path}")
        job(src_path, config)
        queue.task_done()


if __name__ == "__main__":
    t = threading.Thread(
        target=file_processing_worker, kwargs={"queue": queue}, daemon=True
    )
    t.start()

    observer = PollingObserver()
    event_handler = FileEventHandler(config, queue)
    for watch_dir in config.watches:
        observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()
    logger.info(f"開始監控資料夾: {config.watches}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
