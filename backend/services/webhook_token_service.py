"""Webhook token 管理與驗證。

Why: 統一管理 webhook 的靜態 Bearer token（新增/撤銷/命名），明文僅於產生
當下回傳一次，資料庫僅存 SHA-256 雜湊。採相容式強制：無有效 token 時放行，
存在有效 token 時要求合法 Bearer。
"""

from backend import models
from backend.repositories.webhook_token import WebhookTokenRepository
from backend.utils.security import generate_webhook_token, hash_token


class WebhookTokenService:
    def __init__(self, repository: WebhookTokenRepository):
        self.repository = repository

    def list_tokens(self) -> list[models.WebhookToken]:
        return self.repository.get_all()

    def create_token(self, name: str) -> tuple[str, models.WebhookToken]:
        """產生新 token，回傳 (明文, 模型)。明文僅此一次提供。"""
        plaintext, token_hash = generate_webhook_token()
        token = self.repository.create(name, token_hash)
        return plaintext, token

    def revoke_token(self, token_id: str) -> models.WebhookToken | None:
        return self.repository.revoke(token_id)

    def get_token(self, token_id: str) -> models.WebhookToken | None:
        return self.repository.get_by_id(token_id)

    def delete_token(self, token_id: str) -> bool:
        """永久刪除 token，回傳是否有刪除到資料。

        僅供已撤銷的 token 使用；呼叫端需先確認狀態。
        """
        return self.repository.delete(token_id)

    def is_enforced(self) -> bool:
        """是否存在至少一個有效 token（決定 webhook 是否強制驗證）。"""
        return self.repository.count_active() > 0

    def verify(self, token: str) -> bool:
        """驗證明文 token 是否對應到一個未撤銷的 token。"""
        if not token:
            return False
        return self.repository.find_active_by_hash(hash_token(token)) is not None
