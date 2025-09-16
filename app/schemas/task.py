from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    title: str
    description: str
    is_public: bool = False


class TaskInput(TaskBase): ...


class TaskCreate(TaskBase):
    is_completed: bool = False
    user_id: int


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_public: bool | None = None
    is_completed: bool | None = None


class TaskRead(TaskCreate):
    id: int


class TaskFilters(BaseModel):
    limit: int = Field(default=10, le=100, ge=1)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(default="id", validation_alias="sort-by")
    completed: bool | None = None
    public: bool | None = None
    title_contains: str | None = Field(default=None, validation_alias="title-contains")

    model_config = ConfigDict(populate_by_name=True)
