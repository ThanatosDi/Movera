import os


#TODO: 等待 UI/UX 實現在看怎麼做
class PathService:
    def __init__(self): ...

    def selector(self, path: str):
        for root, dirs, files in os.walk(path):
            ...
