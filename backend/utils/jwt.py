"""JWT 簽發與驗證工具（HS256，以 HMAC secret 簽章）。

Why: 登入後以 HMAC secret 採 HS256 簽發 JWT 作為 API 存取憑證，
此模組封裝簽發與驗證細節，避免各層直接操作 pyjwt。
"""

from datetime import UTC, datetime, timedelta

import jwt

ALGORITHM = "HS256"
DEFAULT_EXPIRE_HOURS = 12


class InvalidToken(Exception):
    """JWT 簽章無效、過期或格式錯誤。"""


def create_access_token(
    secret: str, subject: str, expires_hours: int = DEFAULT_EXPIRE_HOURS
) -> str:
    """以 HS256 簽發含 sub/iat/exp 的 JWT。"""
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(hours=expires_hours),
    }
    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def decode_access_token(secret: str, token: str) -> dict:
    """驗證並解析 JWT，失敗時拋出 InvalidToken。"""
    try:
        return jwt.decode(token, secret, algorithms=[ALGORITHM])
    except jwt.PyJWTError as exc:
        raise InvalidToken(str(exc)) from exc
