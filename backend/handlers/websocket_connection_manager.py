from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from backend.database import SessionLocal
from backend.handlers.websocket_error_handler import WebSocketErrorHandler
from backend.handlers.websocket_message_processor import WebSocketMessageProcessor
from backend.utils.logger import logger


class WebSocketConnectionManager:
    """WebSocket 連接管理器"""

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.client_info = f"{websocket.client.host}:{websocket.client.port}"
        self.message_processor = WebSocketMessageProcessor(websocket)
        self.error_handler = WebSocketErrorHandler(websocket)
        self.is_connected = False

    @asynccontextmanager
    async def get_db_session(self) -> AsyncGenerator[Session, None]:
        """資料庫 Session 的 Async Context Manager"""
        db: Session = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    async def accept_connection(self):
        """接受 WebSocket 連接"""
        await self.websocket.accept()
        self.is_connected = True
        logger.info(f"WebSocket connection accepted from {self.client_info}")

    async def handle_connection(self):
        """處理整個 WebSocket 連接生命周期"""
        if not self.is_connected:
            await self.accept_connection()

        try:
            await self._message_loop()
        except Exception as e:
            logger.error(f"WebSocket connection error for {self.client_info}: {e}")
        finally:
            self.is_connected = False
            logger.info(f"WebSocket connection closed for {self.client_info}")

    async def _message_loop(self):
        """主要的消息循環"""
        while self.is_connected:
            try:
                # 接收訊息
                data = await self.websocket.receive_json()
                logger.debug(f"Received data from {self.client_info}: {data}")

                # 使用 async context manager 管理資料庫 session
                async with self.get_db_session() as db:
                    success = await self.message_processor.process_message(data, db)
                    if not success:
                        logger.debug(f"Message processing failed for {self.client_info}")

            except WebSocketDisconnect:
                logger.info(f"Client {self.client_info} disconnected normally")
                self.is_connected = False
                break

            except Exception as e:
                # 接收訊息時的錯誤（如 JSON 解析錯誤）
                await self._handle_receive_error(e)

    async def _handle_receive_error(self, error: Exception):
        """處理接收訊息時的錯誤"""
        try:
            await self.error_handler.handle_message_error(error, self.client_info)
        except Exception:
            # 如果連錯誤訊息都無法發送，可能是連線已中斷
            logger.error(f"Failed to send error response to {self.client_info}")
            self.is_connected = False

    async def disconnect(self):
        """主動斷開連接"""
        if self.is_connected:
            try:
                await self.websocket.close()
            except Exception as e:
                logger.error(f"Error closing websocket for {self.client_info}: {e}")
            finally:
                self.is_connected = False