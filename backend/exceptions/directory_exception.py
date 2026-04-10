class DirectoryNotFound(Exception):
    """
    目錄不存在時引發的例外。
    """

    def __init__(self, path: str):
        self.path = path
        super().__init__(f"目錄不存在: '{path}'")


class DirectoryAccessDenied(Exception):
    """
    無權存取目錄時引發的例外。
    """

    def __init__(self, path: str):
        self.path = path
        super().__init__(f"無權存取此目錄: '{path}'")
