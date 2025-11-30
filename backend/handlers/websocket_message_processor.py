from typing import Any, Dict

from fastapi import WebSocket
from pydantic import ValidationError
from sqlalchemy.orm import Session

from backend.exceptions.wsException import UnHandledWebSocketEvent
from backend.handlers.websocket_error_handler import WebSocketErrorHandler
from backend.repositories.log import LogRepository
from backend.repositories.setting import SettingRepository
from backend.repositories.task import TaskRepository
from backend.schemas import WebSocketMessage
from backend.services.logService import LogService
from backend.services.previewService import ParsePreviewService, RegexPreviewService
from backend.services.settingService import SettingService
from backend.services.taskService import TaskService
from backend.services.wsService import WSServices, wsService
from backend.utils.logger import logger


class WebSocketMessageProcessor:
    """WebSocket 消息處理器"""

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.error_handler = WebSocketErrorHandler(websocket)

    def create_services(self, db: Session) -> WSServices:
        """建立所有需要的服務實例"""
        # 建立 Repository 層
        task_repo = TaskRepository(db=db)
        setting_repo = SettingRepository(db=db)
        log_repo = LogRepository(db=db)

        # 建立 Service 層
        task_service = TaskService(repository=task_repo)
        setting_service = SettingService(repository=setting_repo)
        log_service = LogService(repository=log_repo)
        parse_preview_service = ParsePreviewService()
        regex_preview_service = RegexPreviewService()

        # 組裝服務容器
        return WSServices(
            task=task_service,
            setting=setting_service,
            log=log_service,
            parse_preview=parse_preview_service,
            regex_preview=regex_preview_service,
        )

    async def process_message(self, data: Dict[str, Any], db: Session) -> bool:
        """
        處理單一 WebSocket 訊息

        Returns:
            bool: True 表示處理成功，False 表示處理失敗但可繼續，拋出異常表示嚴重錯誤
        """
        # 保存原始資料用於錯誤處理
        request_id = data.get("requestId", None)
        event_name = data.get("event", "unknown")

        try:
            # 驗證訊息格式
            message = WebSocketMessage(**data)
            logger.debug(f"WebSocket message: {message}")

            # 建立服務並處理請求
            services = self.create_services(db)
            ws_service_instance = wsService(services=services)

            # 呼叫事件監聽器
            response = await ws_service_instance.event_listener(
                message.event, message.payload, message.requestId
            )
            logger.debug(f"WebSocket response: {response}")

            # 發送成功響應
            await self.websocket.send_json(response)
            return True

        except ValidationError as e:
            # Pydantic 驗證錯誤
            await self.error_handler.handle_validation_error(e, event_name, request_id)
            return False

        except self.error_handler.get_business_exceptions() as e:
            # 業務邏輯錯誤
            await self.error_handler.handle_business_error(e, event_name, request_id)
            return False

        except UnHandledWebSocketEvent as e:
            # 未處理的事件
            await self.error_handler.handle_unhandled_event_error(
                e, event_name, request_id
            )
            return False

        except Exception as e:
            # 未預期的錯誤
            await self.error_handler.handle_unexpected_error(e, event_name, request_id)
            return False
