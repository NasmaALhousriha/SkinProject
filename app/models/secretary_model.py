from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from .user_model import User
    from .appointment_model import Appointment
    from .notification_model import Notification

class SecretaryProfile(Base):
    __tablename__ = "secretary_profiles"

    secretary_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="secretary_profile")
    # appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="secretary")
    # notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")