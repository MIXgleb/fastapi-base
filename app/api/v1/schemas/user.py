from pydantic import BaseModel

from app.schemas import UserRead


class MessageDeleteUserReturn(BaseModel):
    message: str = "User has been removed successfully."
    user: UserRead
