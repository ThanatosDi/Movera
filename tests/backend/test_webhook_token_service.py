"""WebhookTokenService 測試：產生、列出、撤銷、強制判斷、驗證。"""

from backend.utils.security import WEBHOOK_TOKEN_PREFIX


class TestWebhookTokenService:
    def test_create_returns_plaintext_once_and_stores_hash(
        self, webhook_token_service, webhook_token_repository
    ):
        plaintext, token = webhook_token_service.create_token("qBittorrent")
        assert plaintext.startswith(WEBHOOK_TOKEN_PREFIX)
        stored = webhook_token_repository.get_by_id(token.id)
        # DB 不存明文
        assert stored.token_hash != plaintext
        assert plaintext not in stored.token_hash

    def test_list_tokens(self, webhook_token_service):
        webhook_token_service.create_token("a")
        webhook_token_service.create_token("b")
        names = [t.name for t in webhook_token_service.list_tokens()]
        assert names == ["a", "b"]

    def test_is_enforced_false_when_empty(self, webhook_token_service):
        assert webhook_token_service.is_enforced() is False

    def test_is_enforced_true_after_create(self, webhook_token_service):
        webhook_token_service.create_token("a")
        assert webhook_token_service.is_enforced() is True

    def test_verify_valid_token(self, webhook_token_service):
        plaintext, _ = webhook_token_service.create_token("a")
        assert webhook_token_service.verify(plaintext) is True

    def test_verify_unknown_token(self, webhook_token_service):
        webhook_token_service.create_token("a")
        assert webhook_token_service.verify("movera_unknown") is False

    def test_revoke_invalidates_token(self, webhook_token_service):
        plaintext, token = webhook_token_service.create_token("a")
        webhook_token_service.revoke_token(token.id)
        assert webhook_token_service.verify(plaintext) is False

    def test_revoke_clears_enforcement_when_last(self, webhook_token_service):
        _, token = webhook_token_service.create_token("a")
        webhook_token_service.revoke_token(token.id)
        assert webhook_token_service.is_enforced() is False

    def test_delete_token_removes_from_db(self, webhook_token_service):
        _, token = webhook_token_service.create_token("a")
        webhook_token_service.revoke_token(token.id)
        assert webhook_token_service.delete_token(token.id) is True
        assert webhook_token_service.get_token(token.id) is None
        assert webhook_token_service.list_tokens() == []

    def test_delete_unknown_returns_false(self, webhook_token_service):
        assert webhook_token_service.delete_token("nope") is False
