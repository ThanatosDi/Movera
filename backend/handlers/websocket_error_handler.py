from typing import Optional

from fastapi import WebSocket
from pydantic import ValidationError

from backend.exceptions.taskException import TaskAlreadyExists, TaskNotFound
from backend.exceptions.wsException import (
    PayloadValidationError,
    UnHandledWebSocketEvent,
)
from backend.utils.logger import logger


class WebSocketErrorHandler:
    """WebSocket 錯誤處理器"""

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    async def send_error_response(
        self,
        event: str,
        error_type: str,
        error_message: str,
        request_id: Optional[str] = None,
    ):
        """發送錯誤響應給客戶端"""
        try:
            await self.websocket.send_json(
                {
                    "event": event,
                    "payload": {"error": error_type, "message": error_message},
                    "success": False,
                    "requestId": request_id,
                }
            )
        except Exception as e:
            logger.error(f"Failed to send error response: {e}")

    async def handle_validation_error(
        self, error: ValidationError, event_name: str, request_id: Optional[str]
    ):
        """處理驗證錯誤"""
        logger.warning(f"Validation error: {error}")
        await self.send_error_response(
            event_name,
            "ValidationError",
            f"Invalid message format: {str(error)}",
            request_id,
        )

    async def handle_business_error(
        self,
        error: Exception,
        event_name: str,
        request_id: Optional[str],
    ):
        """處理業務邏輯錯誤"""
        logger.warning(f"Business logic error: {type(error).__name__}: {error}")
        await self.send_error_response(
            event_name, type(error).__name__, str(error), request_id
        )

    async def handle_unhandled_event_error(
        self, error: UnHandledWebSocketEvent, event_name: str, request_id: Optional[str]
    ):
        """處理未處理的事件錯誤"""
        logger.warning(f"未處理的 WebSocket 事件: {error.event}")
        await self.send_error_response(
            event_name,
            "UnHandledWebSocketEvent",
            f"Event '{error.event}' is not handled",
            request_id,
        )

    async def handle_unexpected_error(
        self, error: Exception, event_name: str, request_id: Optional[str]
    ):
        """處理未預期的錯誤"""
        logger.error(f"Unexpected error processing message: {error}", exc_info=True)
        await self.send_error_response(
            event_name,
            "InternalServerError",
            "An unexpected error occurred",
            request_id,
        )

    async def handle_message_error(self, error: Exception, client_info: str):
        """處理消息接收錯誤"""
        logger.error(f"Error receiving message from {client_info}: {error}")
        await self.send_error_response(
            "unknown",
            "MessageReceiveError",
            "Failed to process message",
            None,
        )

    def get_business_exceptions(self) -> tuple:
        """獲取需要特殊處理的業務異常類型"""
        return (
            ValueError,
            NotImplementedError,
            TaskAlreadyExists,
            TaskNotFound,
            PayloadValidationError,
        )