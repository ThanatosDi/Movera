from fastapi import APIRouter, WebSocket

from backend.handlers.websocket_connection_manager import WebSocketConnectionManager

router = APIRouter(
    tags=["Websocket"],
)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 端點處理函數

    使用 WebSocketConnectionManager 來管理整個連接生命周期，
    包括連接接受、消息處理和錯誤處理。
    """
    connection_manager = WebSocketConnectionManager(websocket)
    await connection_manager.handle_connection()
