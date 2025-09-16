from fastapi import APIRouter

from app.api.v1.schemas import MessageHealthCheckReturn
from app.core.config import settings

router = APIRouter(prefix=settings.api.v1.health, tags=["Health"])


@router.get("/check")
def health_check() -> MessageHealthCheckReturn:
    """
    Check the health of the service.

    Returns:
        MessageHealthCheckReturn: status message

    """
    return MessageHealthCheckReturn()
