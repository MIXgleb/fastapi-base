from fastapi import APIRouter, Depends
from fastapi_limiter.depends import RateLimiter

from app.api.v1 import router as router_api_v1
from app.core.config import settings

router = APIRouter(prefix=settings.api.prefix, dependencies=[Depends(RateLimiter(seconds=5))])
router.include_router(router_api_v1)
