"""Worker 模組專用例外類別"""


class RenameOperationError(Exception):
    """重命名操作失敗時引發的例外"""

    def __init__(self, filepath: str, reason: str):
        self.filepath = filepath
        self.reason = reason
        super().__init__(f"重命名失敗: {filepath}, 原因: {reason}")


class MoveOperationError(Exception):
    """移動操作失敗時引發的例外"""

    def __init__(self, filepath: str, destination: str, reason: str):
        self.filepath = filepath
        self.destination = destination
        self.reason = reason
        super().__init__(f"移動失敗: {filepath} -> {destination}, 原因: {reason}")
