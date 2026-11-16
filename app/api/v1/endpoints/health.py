from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/healthz", summary="Health check")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
    }
