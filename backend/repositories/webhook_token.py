from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend import models


class WebhookTokenRepository:
    """Webhook token 的資料存取層。"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[models.WebhookToken]:
        return (
            self.db.query(models.WebhookToken)
            .order_by(models.WebhookToken.created_at.asc())
            .all()
        )

    def get_by_id(self, token_id: str) -> models.WebhookToken | None:
        return (
            self.db.query(models.WebhookToken)
            .filter(models.WebhookToken.id == token_id)
            .first()
        )

    def create(self, name: str, token_hash: str) -> models.WebhookToken:
        token = models.WebhookToken(name=name, token_hash=token_hash)
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def delete(self, token_id: str) -> bool:
        """永久刪除 token，回傳是否有刪除到資料。"""
        token = self.get_by_id(token_id)
        if token is None:
            return False
        self.db.delete(token)
        self.db.commit()
        return True

    def revoke(self, token_id: str) -> models.WebhookToken | None:
        token = self.get_by_id(token_id)
        if token and token.revoked_at is None:
            token.revoked_at = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(token)
        return token

    def count_active(self) -> int:
        """有效（未撤銷）token 的數量。"""
        return (
            self.db.query(models.WebhookToken)
            .filter(models.WebhookToken.revoked_at.is_(None))
            .count()
        )

    def find_active_by_hash(self, token_hash: str) -> models.WebhookToken | None:
        """以雜湊查詢未撤銷的 token。"""
        return (
            self.db.query(models.WebhookToken)
            .filter(
                models.WebhookToken.token_hash == token_hash,
                models.WebhookToken.revoked_at.is_(None),
            )
            .first()
        )
