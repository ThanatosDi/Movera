class TaskAlreadyExists(Exception):
    """
    任務已存在時引發的例外。
    """

    def __init__(self, task_name: str):
        self.task_name = task_name
        super().__init__(f"Task name: '{task_name}' already exists")


class TaskNotFound(Exception):
    """
    任務不存在時引發的例外。
    """

    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task Id: '{task_id}' not found")
