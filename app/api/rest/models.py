from fastapi import APIRouter

from app.api.rest.user_endpoints import router as users_router
from app.api.rest.auth import router as auth_router
from app.core.config import settings

api_router = APIRouter(prefix=settings.API_PREFIX)
api_router.include_router(auth_router, tags=["authentication"])
api_router.include_router(users_router, prefix="/v1", tags=["users"])