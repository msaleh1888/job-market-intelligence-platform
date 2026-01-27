from fastapi import APIRouter

from jmip_api.core.config import settings

router = APIRouter(tags=["system"])


@router.get("/version")
def version():
    return {
        "name": settings.app_name,
        "version": settings.version,
        "commit": settings.commit,
        "env": settings.env,
    }
