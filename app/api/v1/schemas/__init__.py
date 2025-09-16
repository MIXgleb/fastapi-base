__all__ = (
    "MessageDeleteTaskReturn",
    "MessageDeleteUserReturn",
    "MessageHealthCheckReturn",
    "MessageLoginReturn",
    "MessageRegisterReturn",
    "MessageUpdateTaskReturn",
)


from app.api.v1.schemas.auth import MessageLoginReturn, MessageRegisterReturn
from app.api.v1.schemas.health import MessageHealthCheckReturn
from app.api.v1.schemas.task import MessageDeleteTaskReturn, MessageUpdateTaskReturn
from app.api.v1.schemas.user import MessageDeleteUserReturn
