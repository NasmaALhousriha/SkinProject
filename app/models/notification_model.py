# notification
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from .user_model import User


class Notification(Base):
    __tablename__ = "notifications"

    # Columns
    notification_id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Foreign Key
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="notifications")






