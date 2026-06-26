"""SecretService 測試：env 優先、DB 持久化、重啟沿用。"""

from backend.services.secret_service import SECRET_SETTING_KEY, SecretService


class TestSecretService:
    def test_env_secret_takes_precedence_and_not_persisted(
        self, secret_service, setting_repository, monkeypatch
    ):
        monkeypatch.setenv("MOVERA_SECRET_KEY", "env-secret")
        assert secret_service.resolve_secret() == "env-secret"
        # 不應寫入 DB
        assert setting_repository.get(SECRET_SETTING_KEY) is None

    def test_autogenerate_and_persist_when_missing(
        self, secret_service, setting_repository, monkeypatch
    ):
        monkeypatch.delenv("MOVERA_SECRET_KEY", raising=False)
        secret = secret_service.resolve_secret()
        assert secret
        stored = setting_repository.get(SECRET_SETTING_KEY)
        assert stored is not None and stored.value == secret

    def test_reuse_persisted_secret_on_restart(
        self, setting_repository, monkeypatch
    ):
        monkeypatch.delenv("MOVERA_SECRET_KEY", raising=False)
        first = SecretService(setting_repository).resolve_secret()
        # 模擬重啟：新服務實例，同一 DB
        second = SecretService(setting_repository).resolve_secret()
        assert first == second
