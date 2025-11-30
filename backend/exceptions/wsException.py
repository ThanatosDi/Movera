class UnHandledWebSocketEvent(Exception):
    """
    當收到未處理的 WebSocket 事件時引發的例外。
    """

    def __init__(self, event: str):
        self.event = event
        super().__init__(f"未處理的 WebSocket 事件: {event}")


class PayloadValidationError(Exception):
    """
    當 WebSocket 訊息的 payload 驗證失敗時引發的例外。
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(f"Payload Validation Error: {message}")
