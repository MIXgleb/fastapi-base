from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.tasks import router as task_router
from app.api.v1.endpoints.users import router as user_router
from app.core.config import settings

router = APIRouter(prefix=settings.api.v1.prefix)
router.include_router(auth_router)
router.include_router(task_router)
router.include_router(user_router)
