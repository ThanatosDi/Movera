"""AuthService 測試：建立帳號、登入驗證、env seed、JWT。"""

from backend.utils.jwt import decode_access_token
from backend.utils.security import sha256_hex


class TestAuthService:
    def test_needs_setup_when_empty(self, auth_service):
        assert auth_service.needs_setup() is True

    def test_create_admin_stores_no_plaintext(self, auth_service, user_repository):
        pw = sha256_hex("password")
        auth_service.create_admin("admin", pw)
        user = user_repository.get_by_username("admin")
        assert user is not None
        assert user.salt
        # 儲存的雜湊不等於前端值，也不含明文
        assert user.password_hash != pw
        assert "password" not in user.password_hash
        assert auth_service.needs_setup() is False

    def test_verify_credentials_success(self, auth_service):
        pw = sha256_hex("hunter2")
        auth_service.create_admin("admin", pw)
        assert auth_service.verify_credentials("admin", pw) is True

    def test_verify_credentials_wrong_password(self, auth_service):
        auth_service.create_admin("admin", sha256_hex("hunter2"))
        assert auth_service.verify_credentials("admin", sha256_hex("wrong")) is False

    def test_verify_credentials_unknown_user(self, auth_service):
        assert auth_service.verify_credentials("ghost", sha256_hex("x")) is False

    def test_issue_token_decodable(self, auth_service):
        token = auth_service.issue_token("admin")
        payload = decode_access_token("test-secret", token)
        assert payload["sub"] == "admin"

    def test_seed_admin_from_env_creates_account(self, auth_service):
        auth_service.seed_admin_from_env("envadmin", "envpass")
        # env 密碼為明文，登入時前端送 sha256(明文)
        assert auth_service.verify_credentials("envadmin", sha256_hex("envpass")) is True

    def test_seed_admin_from_env_skips_when_account_exists(
        self, auth_service, user_repository
    ):
        auth_service.create_admin("existing", sha256_hex("p"))
        auth_service.seed_admin_from_env("envadmin", "envpass")
        assert user_repository.get_by_username("envadmin") is None
