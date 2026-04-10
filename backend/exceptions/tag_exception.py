class TagAlreadyExists(Exception):
    """標籤已存在時引發的例外。"""

    def __init__(self, tag_name: str):
        self.tag_name = tag_name
        super().__init__(f"Tag name: '{tag_name}' already exists")


class TagNotFound(Exception):
    """標籤不存在時引發的例外。"""

    def __init__(self, tag_id: str):
        self.tag_id = tag_id
        super().__init__(f"Tag Id: '{tag_id}' not found")


class InvalidTagColor(Exception):
    """標籤顏色無效時引發的例外。"""

    def __init__(self, color: str):
        self.color = color
        super().__init__(f"Invalid tag color: '{color}'")
