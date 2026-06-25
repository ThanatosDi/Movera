"""security 與 jwt 工具測試。"""

import pytest

from backend.utils import jwt as jwt_utils
from backend.utils.security import (
    WEBHOOK_TOKEN_PREFIX,
    generate_salt,
    generate_secret,
    generate_webhook_token,
    hash_password,
    hash_token,
    sha256_hex,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_password_deterministic_with_same_salt(self):
        salt = "abc123"
        received = sha256_hex("password")
        assert hash_password(received, salt) == hash_password(received, salt)

    def test_hash_password_differs_by_salt(self):
        received = sha256_hex("password")
        assert hash_password(received, "salt1") != hash_password(received, "salt2")

    def test_verify_password_success(self):
        salt = generate_salt()
        received = sha256_hex("secret")
        ph = hash_password(received, salt)
        assert verify_password(received, salt, ph) is True

    def test_verify_password_failure(self):
        salt = generate_salt()
        ph = hash_password(sha256_hex("secret"), salt)
        assert verify_password(sha256_hex("wrong"), salt, ph) is False

    def test_no_plaintext_in_hash(self):
        ph = hash_password(sha256_hex("mypassword"), generate_salt())
        assert "mypassword" not in ph


class TestWebhookToken:
    def test_generate_webhook_token_prefix(self):
        plaintext, _ = generate_webhook_token()
        assert plaintext.startswith(WEBHOOK_TOKEN_PREFIX)

    def test_generate_webhook_token_hash_matches(self):
        plaintext, token_hash = generate_webhook_token()
        assert hash_token(plaintext) == token_hash

    def test_tokens_are_unique(self):
        t1, _ = generate_webhook_token()
        t2, _ = generate_webhook_token()
        assert t1 != t2


class TestSecret:
    def test_generate_secret_nonempty_unique(self):
        assert generate_secret() != generate_secret()


class TestJwt:
    def test_roundtrip(self):
        secret = "test-secret"
        token = jwt_utils.create_access_token(secret, subject="admin")
        payload = jwt_utils.decode_access_token(secret, token)
        assert payload["sub"] == "admin"
        assert "exp" in payload

    def test_wrong_secret_rejected(self):
        token = jwt_utils.create_access_token("secret-a", subject="admin")
        with pytest.raises(jwt_utils.InvalidToken):
            jwt_utils.decode_access_token("secret-b", token)

    def test_expired_token_rejected(self):
        secret = "test-secret"
        token = jwt_utils.create_access_token(secret, subject="admin", expires_hours=-1)
        with pytest.raises(jwt_utils.InvalidToken):
            jwt_utils.decode_access_token(secret, token)

    def test_tampered_token_rejected(self):
        secret = "test-secret"
        token = jwt_utils.create_access_token(secret, subject="admin")
        with pytest.raises(jwt_utils.InvalidToken):
            jwt_utils.decode_access_token(secret, token + "x")
