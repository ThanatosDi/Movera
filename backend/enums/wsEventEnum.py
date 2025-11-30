from enum import Enum


class wsEventEnum(str, Enum):
    # 系統狀態事件
    STATUS = "system:status"
    PING = "system:ping"
    # 任務事件
    GET_TASKS = "get:tasks"
    GET_TASK = "get:task"
    CREATE_TASK = "create:task"
    DELETE_TASK = "delete:task"
    UPDATE_TASK = "update:task"
    STATS_TASKS = "stats:tasks"
    # 日誌事件
    GET_LOGS = "get:logs"
    CREATE_LOG = "create:log"
    # 設定事件
    GET_SETTINGS = "get:settings"
    UPDATE_SETTINGS = "update:settings"
    # 預覽事件
    PREVIEW_PARSE = "preview:parse"
    PREVIEW_REGEX = "preview:regex"

    @classmethod
    def has_value(cls, item: str) -> bool:
        return item in cls._value2member_map_
