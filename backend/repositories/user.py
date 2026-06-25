from sqlalchemy.orm import Session

from backend import models


class UserRepository:
    """管理員帳號的資料存取層。"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> models.User | None:
        return (
            self.db.query(models.User)
            .filter(models.User.username == username)
            .first()
        )

    def count(self) -> int:
        return self.db.query(models.User).count()

    def create(self, username: str, password_hash: str, salt: str) -> models.User:
        user = models.User(
            username=username, password_hash=password_hash, salt=salt
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
