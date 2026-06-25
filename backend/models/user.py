from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, String

from backend.database import Base


class User(Base):
    """管理員帳號。

    Why: 系統採單一管理員模式，密碼以「前端 SHA-256 值 + 每帳號 salt」再經
    SHA-256 雜湊後儲存，資料庫不保存任何明文密碼。
    """

    __tablename__ = "user"

    username = Column(String, primary_key=True, comment="管理員使用者名稱")
    password_hash = Column(
        String, nullable=False, comment="sha256(salt + 前端傳入的 sha256 值)"
    )
    salt = Column(String, nullable=False, comment="每帳號隨機 salt")
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC),
        comment="建立時間",
    )

    def __repr__(self):
        return f"<User(username={self.username})>"
