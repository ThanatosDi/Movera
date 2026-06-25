import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, String

from backend.database import Base


class WebhookToken(Base):
    """Webhook 靜態 Bearer token。

    Why: Webhook 來自下載器無法登入，需獨立的靜態 token。資料庫僅儲存 token
    的 SHA-256 雜湊，明文（movera_ 前綴）僅於產生當下回傳一次。
    """

    __tablename__ = "webhook_token"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        index=True,
        nullable=False,
    )
    name = Column(String, nullable=False, comment="token 名稱（識別用途）")
    token_hash = Column(
        String, nullable=False, unique=True, index=True, comment="sha256(明文 token)"
    )
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        comment="建立時間",
    )
    revoked_at = Column(
        DateTime, nullable=True, default=None, comment="撤銷時間，NULL 表示有效"
    )

    def __repr__(self):
        return f"<WebhookToken(id={self.id}, name={self.name})>"
