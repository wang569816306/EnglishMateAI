from fastapi import APIRouter
from app.settings import settings

router = APIRouter(tags=["健康检查"])

@router.get("/")
async def health_check():
    return {
        "status": "ok",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION
    }