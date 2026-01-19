from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional, TypeVar

from pydantic import BaseModel

from backend import schemas
from backend.enums.wsEventEnum import wsEventEnum
from backend.exceptions.wsException import (
    PayloadValidationError,
    UnHandledWebSocketEvent,
)
from backend.services.logService import LogService
from backend.services.previewService import ParsePreviewService, RegexPreviewService
from backend.services.settingService import SettingService
from backend.services.taskService import TaskService
from backend.utils.logger import logger


@dataclass
class WSServices:
    """一個用來集中管理 WebSocket 服務所需依賴項的容器。"""

    task: TaskService
    setting: SettingService
    log: LogService
    parse_preview: ParsePreviewService
    regex_preview: RegexPreviewService


# 定義處理函式的型別提示
EventHandler = Callable[..., Awaitable[Any]]
_event_handlers: Dict[str, EventHandler] = {}

# 泛型型別變數，用於 payload 驗證
T = TypeVar("T", bound=BaseModel)


def register_event_handler(event: str):
    """一個裝飾器，用於為特定事件註冊處理函式。"""

    def decorator(func: EventHandler):
        _event_handlers[event] = func
        return func

    return decorator


class wsService:
    """
    WebSocket 業務邏輯服務，使用處理器註冊模式來分派事件。
    """

    def __init__(self, services: WSServices):
        self.services = services
        self._event_handlers = _event_handlers
        logger.debug(f"wsEvent handlers : {self._event_handlers}")

    def _validate_payload(
        self, schema_class: type[T], payload: dict, error_prefix: str = "Invalid payload"
    ) -> T:
        """
        統一的 payload 驗證方法

        Args:
            schema_class: Pydantic schema 類別
            payload: 要驗證的 payload 字典
            error_prefix: 錯誤訊息前綴

        Returns:
            驗證後的 schema 實例

        Raises:
            ValueError: 如果 payload 驗證失敗
        """
        try:
            return schema_class(**payload)
        except Exception as e:
            raise ValueError(f"{error_prefix}: {e}")

    async def event_listener(
        self,
        event: str,
        payload: Any,
        request_id: Optional[str],
    ):
        """
        事件分派器。
        """
        if not wsEventEnum.has_value(event):
            raise UnHandledWebSocketEvent(event)

        handler = self._event_handlers.get(event)
        if not handler:
            raise NotImplementedError(f"Event: '{event}' handler not registered")

        response = await handler(self, payload)
        return {
            "event": f"{event}",
            "payload": response,
            "success": True,
            "requestId": request_id,
        }

    @register_event_handler(wsEventEnum.PING)
    async def _handle_system_ping(
        self,
        payload: Any,
    ) -> dict[str, str]:
        """處理系統 PING 事件，只回傳 payload。"""
        return {"message": "pong"}

    @register_event_handler(wsEventEnum.GET_TASKS)
    async def _handle_get_tasks(
        self,
        payload: Any,
    ) -> list[dict[str, str | list[dict[str, str | int]] | bool]]:
        """處理獲取任務列表的事件"""
        tasks = self.services.task.get_all_tasks()
        return [
            schemas.Task.model_validate(orm_task).model_dump(mode="json")
            for orm_task in tasks
        ]

    @register_event_handler(wsEventEnum.CREATE_TASK)
    async def _handle_create_task(
        self, payload: dict[str, str]
    ) -> dict[str, str | list | bool]:
        """
        處理創建任務的事件。

        Args:
            payload (Any): 創建任務的資料

        Returns:
            Dict[str, Any]: 創建的任務的資料

        Raises:
            ValueError: 如果傳入的任務資料無效
        """
        task = self._validate_payload(schemas.TaskCreate, payload, "Invalid task data")
        response = self.services.task.create_task(task)
        return schemas.Task.model_validate(response).model_dump(mode="json")

    @register_event_handler(wsEventEnum.UPDATE_TASK)
    async def _handle_update_task(
        self, payload: dict[str, str]
    ) -> dict[str, str | list | bool]:
        """
        處理更新任務的事件。

        Args:
            payload (dict[str, str]): 更新任務的資料

        Returns:
            dict[str, str | list | bool]: 更新的任務的資料

        Raises:
            ValueError: 如果傳入的任務資料無效
        """
        if "id" not in payload:
            raise ValueError("Invalid task data: missing 'id' field")
        task_id = payload.pop("id")
        task_update = self._validate_payload(schemas.TaskUpdate, payload, "Invalid task data")
        response = self.services.task.update_task(task_id, task_update)
        return schemas.Task.model_validate(response).model_dump(mode="json")

    @register_event_handler(wsEventEnum.DELETE_TASK)
    async def _handle_delete_task(self, payload: dict[str, str]) -> None:
        """
        處理刪除任務的事件。

        Args:
            payload (dict[str, str]): 刪除任務的資料

        Raises:
            ValueError: 如果傳入的任務資料無效
        """
        if "id" not in payload:
            raise ValueError("Invalid task id: missing 'id' field")
        self.services.task.delete_task(payload["id"])

    @register_event_handler(wsEventEnum.GET_SETTINGS)
    async def _handle_get_settings(self, payload: Any) -> dict[str, str]:
        """
        處理獲取設定列表的事件。

        Returns:
            dict[str, str]: 設定列表的資料，格式為 {key: value}
        """
        settings = self.services.setting.get_all_settings()
        return settings

    @register_event_handler(wsEventEnum.UPDATE_SETTINGS)
    async def _handle_update_settings(self, payload: dict[str, str]):
        """
        處理更新設定的事件。

        Args:
            payload (dict[str, str]): 要更新的設定資料

        Returns:
            dict[str, str]: 更新後的設定資料
        """
        self.services.setting.update_settings(payload)
        settings = self.services.setting.get_all_settings()
        return settings

    @register_event_handler(wsEventEnum.GET_LOGS)
    async def _handle_get_logs(self, payload: dict[str, str]):
        """
        處理獲取任務 Log 的事件。

        Args:
            payload (dict[str, str]): 要獲取 Log 的資料

        Returns:
            list[dict[str, str | int]]: 任務 Log 資料

        Raises:
            ValueError: 如果傳入的 payload 任務資料無效
        """
        try:
            task_id = payload.get("id")
        except Exception as e:
            raise ValueError(f"Invalid task id: {e}")
        logs = self.services.log.get_logs_by_task_id(task_id)
        return [schemas.Log.model_validate(log).model_dump(mode="json") for log in logs]

    @register_event_handler(wsEventEnum.CREATE_LOG)
    async def _handle_create_log(self, payload: dict[str, str]):
        """
        處理創建任務 Log 的事件。

        Args:
            payload (dict[str, str]): 創建 Log 的資料

        Returns:
            dict[str, str | int]: 創建的 Log 資料

        Raises:
            ValueError: 如果傳入的 payload Log 資料無效
        """
        log = self._validate_payload(schemas.LogCreate, payload, "Invalid log data")
        response = self.services.log.create_log(log)
        logger.info(schemas.Log.model_validate(response).model_dump(mode="json"))
        return schemas.Log.model_validate(response).model_dump(mode="json")

    def _validate_preview_payload(
        self, schema_class: type[T], payload: dict, error_prefix: str
    ) -> T:
        """
        Preview 專用的 payload 驗證方法

        Args:
            schema_class: Pydantic schema 類別
            payload: 要驗證的 payload 字典
            error_prefix: 錯誤訊息前綴

        Returns:
            驗證後的 schema 實例

        Raises:
            PayloadValidationError: 如果 payload 驗證失敗
        """
        try:
            return schema_class(**payload)
        except Exception:
            raise PayloadValidationError(f"{error_prefix}: {payload}")

    @register_event_handler(wsEventEnum.PREVIEW_PARSE)
    async def _handle_preview_parse(self, payload: dict[str, str]):
        validated = self._validate_preview_payload(
            schemas.ParsePreviewRequest, payload, "Invalid parse preview data"
        )
        preview = self.services.parse_preview.preview(
            src_pattern=validated.src_pattern,
            text=validated.text,
            dst_pattern=validated.dst_pattern,
        )
        return preview

    @register_event_handler(wsEventEnum.PREVIEW_REGEX)
    async def _handle_preview_regex(self, payload: dict[str, str]):
        validated = self._validate_preview_payload(
            schemas.RegexPreviewRequest, payload, "Invalid regex preview data"
        )
        preview = self.services.regex_preview.preview(
            src_pattern=validated.src_pattern,
            text=validated.text,
            dst_pattern=validated.dst_pattern,
        )
        return preview
