import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from app.config import settings
from app.database import Base  # noqa: F401
import app.models  # noqa: F401 - registers all models

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_online():
    connectable = create_async_engine(settings.DATABASE_URL)

    async def run():
        async with connectable.connect() as conn:
            await conn.run_sync(
                lambda sync_conn: context.configure(
                    connection=sync_conn,
                    target_metadata=target_metadata,
                    compare_type=True,
                )
            )
            async with conn.begin():
                await conn.run_sync(lambda c: context.run_migrations())

    asyncio.run(run())


run_migrations_online()
