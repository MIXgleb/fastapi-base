from pydantic import BaseModel

from app.schemas import TaskRead


class MessageDeleteTaskReturn(BaseModel):
    message: str = "Task has been removed successfully."
    task: TaskRead


class MessageUpdateTaskReturn(BaseModel):
    message: str = "Task has been updated successfully."
    task: TaskRead
