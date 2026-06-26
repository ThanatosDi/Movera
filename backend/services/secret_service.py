"""HMAC secret 解析與持久化。

Why: JWT 簽章需要一組穩定的 secret。優先序為
環境變數 MOVERA_SECRET_KEY → SQLite setting('secret_key') → 自動產生並持久化，
確保重啟後既發 JWT 仍可驗證；env 設定的 secret 不寫入資料庫，避免雙來源衝突。
"""

from backend.repositories.setting import SettingRepository
from backend.utils.env_config import get_env_secret_key
from backend.utils.security import generate_secret

SECRET_SETTING_KEY = "secret_key"


class SecretService:
    def __init__(self, repository: SettingRepository):
        self.repository = repository

    def resolve_secret(self) -> str:
        """依優先序取得 secret，必要時自動產生並持久化至 SQLite。"""
        env_secret = get_env_secret_key()
        if env_secret:
            return env_secret

        setting = self.repository.get(SECRET_SETTING_KEY)
        if setting and setting.value:
            return setting.value

        secret = generate_secret()
        self.repository.create_or_update(SECRET_SETTING_KEY, secret)
        return secret
