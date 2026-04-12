from backend.utils.logger import logger


class DirectoryNotFound(Exception):
    """
    目錄不存在時引發的例外。
    """

    def __init__(self, path: str):
        self.path = path
        logger.warning(f"目錄不存在: '{path}'")
        super().__init__("目錄不存在")


class DirectoryAccessDenied(Exception):
    """
    無權存取目錄時引發的例外。
    """

    def __init__(self, path: str):
        self.path = path
        logger.warning(f"無權存取此目錄: '{path}'")
        super().__init__("無權存取此目錄")
