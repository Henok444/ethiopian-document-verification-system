from fastapi import APIRouter
from app.api.v1.endpoints import health, verification

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(verification.router, tags=["Verification"])
