from pydantic import BaseModel


class MessageHealthCheckReturn(BaseModel):
    message: str = "Success."
