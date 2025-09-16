from typing import final

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import String

from app.database.models.base import Base
from app.database.models.mixins.int_id_pk import IntIdPkMixin


@final
class Task(IntIdPkMixin, Base):
    title: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(100), nullable=False)
    is_public: Mapped[bool] = mapped_column(nullable=False, default=False)
    is_completed: Mapped[bool] = mapped_column(nullable=False, default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user = relationship("User", back_populates="tasks")
