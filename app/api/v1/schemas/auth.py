from pydantic import BaseModel


class MessageRegisterReturn(BaseModel):
    message: str = "New user created."


class MessageLoginReturn(BaseModel):
    message: str = "Logged in successfully."
