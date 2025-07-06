from queue import Queue

from loguru import logger
from watchdog.events import FileSystemEventHandler

from .model import Config
from .utils import wait_until_file_stable


class FileEventHandler(FileSystemEventHandler):
    def __init__(self, config: Config, queue: Queue):
        self.config = config
        self.queue = queue

    def on_created(self, event):
        if not event.is_directory:
            if wait_until_file_stable(event.src_path) is True:
                logger.info(f"Created: {event.src_path}")
                self.queue.put(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            logger.info(f"Deleted: {event.src_path}")

    def on_modified(self, event):
        if not event.is_directory:
            if wait_until_file_stable(event.src_path) is True:
                logger.info(f"Modified: {event.src_path}")
                self.queue.put(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            logger.info(f"檔案已寫入完成並關閉: {event.src_path}")

    def on_closed(self, event):
        if not event.is_directory:
            logger.info(f"檔案已寫入完成並關閉: {event.src_path}")
