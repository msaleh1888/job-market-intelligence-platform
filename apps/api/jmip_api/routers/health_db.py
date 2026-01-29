from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from jmip_api.core.dependencies import get_db_session

router = APIRouter(tags=["system"])


@router.get("/health/db")
async def health_db(db: AsyncSession = Depends(get_db_session)):  # noqa: B008
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as err:
        raise HTTPException(status_code=503, detail="Database unavailable") from err
