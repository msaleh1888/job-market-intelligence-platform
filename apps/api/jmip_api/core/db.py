from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from jmip_api.core.config import settings

# Engine = connection pool + DB gateway (created once per process)
engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,  # checks connections before using them (helps with stale connections)
)

# Session factory = creates AsyncSession objects on demand
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
