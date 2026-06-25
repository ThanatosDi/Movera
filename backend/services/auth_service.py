"""管理員帳號與登入流程。

Why: 封裝單一管理員帳號的建立、密碼驗證與 JWT 簽發。密碼以
「前端 SHA-256 值 + 每帳號 salt」再經 SHA-256 雜湊儲存，資料庫不保存明文。
"""

from backend import models
from backend.repositories.user import UserRepository
from backend.utils.jwt import create_access_token
from backend.utils.logger import logger
from backend.utils.security import (
    generate_salt,
    hash_password,
    sha256_hex,
    verify_password,
)


class AuthService:
    def __init__(self, repository: UserRepository, secret: str):
        self.repository = repository
        self.secret = secret

    def needs_setup(self) -> bool:
        """資料庫尚無任何管理員帳號時回傳 True。"""
        return self.repository.count() == 0

    def create_admin(self, username: str, password_sha256: str) -> models.User:
        """以前端傳入的 sha256(password) 建立管理員帳號。"""
        salt = generate_salt()
        password_hash = hash_password(password_sha256, salt)
        return self.repository.create(username, password_hash, salt)

    def verify_credentials(self, username: str, password_sha256: str) -> bool:
        """驗證帳號與密碼（password_sha256 為前端傳入的 sha256 值）。"""
        user = self.repository.get_by_username(username)
        if user is None:
            return False
        return verify_password(password_sha256, user.salt, user.password_hash)

    def issue_token(self, username: str) -> str:
        """簽發 JWT 存取憑證。"""
        return create_access_token(self.secret, subject=username)

    def seed_admin_from_env(self, username: str, plaintext_password: str) -> None:
        """以環境變數預設值建立帳號（僅在資料庫無帳號時）。

        env 提供的是明文密碼，後端先做 SHA-256 以對齊前端傳輸格式，
        再加 salt 雜湊儲存。
        """
        if not self.needs_setup():
            return
        password_sha256 = sha256_hex(plaintext_password)
        self.create_admin(username, password_sha256)
        logger.info(f"已依環境變數建立管理員帳號：{username}")
