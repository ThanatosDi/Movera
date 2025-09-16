import logging
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# 匯入專案的 Loguru 設定，確保 handlers 已經建立
try:
    from core.utils.logger import logger as app_logger  # noqa: F401
except Exception:
    # 若直接匯入失敗，將專案根目錄放入 sys.path 再嘗試
    import sys

    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from core.utils.logger import logger as app_logger  # noqa: F401


class InterceptHandler(logging.Handler):
    """攔截標準 logging 並轉送到 Loguru。"""

    def emit(self, record: logging.LogRecord) -> None:
        from loguru import logger as _logger

        try:
            level = _logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        _logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# 不使用 alembic.ini 的 logging 設定，改導入 Loguru
# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)

# 將 stdlib logging 導流到 Loguru
root_logger = logging.getLogger()
root_logger.handlers = [InterceptHandler()]
root_logger.setLevel(logging.NOTSET)
for name in ("alembic", "sqlalchemy"):
    log = logging.getLogger(name)
    log.handlers = []
    log.propagate = True

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
