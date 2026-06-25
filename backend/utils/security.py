"""密碼、secret 與 webhook token 的雜湊與產生工具。

Why: 集中身分驗證相關的雜湊邏輯，確保資料庫永不保存明文密碼或明文 token，
並提供高強度隨機值產生器供 secret 與 webhook token 使用。
"""

import hashlib
import hmac
import secrets

WEBHOOK_TOKEN_PREFIX = "movera_"


def generate_salt() -> str:
    """產生隨機 salt（hex 字串）。"""
    return secrets.token_hex(16)


def hash_password(received_sha256: str, salt: str) -> str:
    """以 sha256(salt + 前端傳入的 sha256 值) 計算密碼雜湊。

    received_sha256 為前端對明文密碼做 SHA-256 後的 hex 字串。
    """
    return hashlib.sha256((salt + received_sha256).encode("utf-8")).hexdigest()


def verify_password(received_sha256: str, salt: str, password_hash: str) -> bool:
    """以常數時間比對密碼雜湊。"""
    candidate = hash_password(received_sha256, salt)
    return hmac.compare_digest(candidate, password_hash)


def sha256_hex(value: str) -> str:
    """回傳字串的 SHA-256 hex 值（供後端對 env 明文密碼預雜湊使用）。"""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def generate_secret() -> str:
    """產生高強度隨機 secret，供 JWT HS256 簽章使用。"""
    return secrets.token_urlsafe(48)


def generate_webhook_token() -> tuple[str, str]:
    """產生 webhook token。

    回傳 (明文 token, token 雜湊)。明文格式為 ``movera_<隨機>``，
    資料庫僅儲存其 SHA-256 雜湊。
    """
    plaintext = f"{WEBHOOK_TOKEN_PREFIX}{secrets.token_urlsafe(32)}"
    return plaintext, hash_token(plaintext)


def hash_token(token: str) -> str:
    """回傳 webhook token 的 SHA-256 hex 雜湊。"""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
