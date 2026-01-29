from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from jmip_api.core.db import SessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a database session per request.

    - Opens a session
    - Yields it to the endpoint
    - Rolls back if an exception occurs
    - Closes the session at the end
    """
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            # If endpoint raises, ensure the transaction is not left open
            await session.rollback()
            raise
