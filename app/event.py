from queue import Queue

from loguru import logger
from watchdog.events import FileModifiedEvent, FileSystemEventHandler

from .utils import is_file_stable


class FileMonitorHandler(FileSystemEventHandler):
    def __init__(self, queue: Queue):
        self.queue = queue

    def on_created(self, event: FileModifiedEvent):
        if event.is_directory:
            return
        try:
            logger.info(f"觸發 on_created 事件: {event.src_path}")
            if is_file_stable(event.src_path):
                logger.info(f"新增檔案: {event.src_path}，增加 queue")
                self.queue.put(event.src_path)
        except Exception as e:
            logger.error(str(e))

    def on_modified(self, event: FileModifiedEvent):
        if event.is_directory:
            return
        try:
            logger.info(f"觸發 on_modified 事件: {event.src_path}")
            if is_file_stable(event.src_path):
                logger.info(f"修改檔案: {event.src_path}")
        except Exception as e:
            logger.error(str(e))
