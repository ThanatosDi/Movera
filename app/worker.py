import os
from queue import Queue

from loguru import logger

from app.model import Config
from app.utils import match_job, move, read_config, rename


class Worker:
    def __init__(self, queue: Queue):
        self.queue = queue

    def file_processing_worker(self):
        MOVERA_CONFIG = os.getenv("MOVERA_CONFIG")
        while True:
            src_path = self.queue.get()
            config = read_config(MOVERA_CONFIG)
            logger.info(f"處理檔案: {src_path}")
            try:
                self.__job_flow(src_path, config)
            except Exception as e:
                logger.error(f"處理檔案時發生錯誤: {str(e)}")
            finally:
                self.queue.task_done()

    def __job_flow(self, src_path: str, config: Config):
        job = match_job(src_path, config)
        # 沒有 job 符合
        if job is None:
            logger.info(f"沒有符合的 job: {src_path}")
            return
        # 當 dst_filename_regex 和 src_filename_regex 都不為空
        # 代表使用者需要將檔案重新命名
        if job.dst_filename_regex is not None and job.src_filename_regex is not None:
            src_path = rename(src_path, job)
        move(src_path, job)
