# app/models/specialist_model.py
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from .device_model import Device

class Specialist(Base):
    __tablename__ = "specialists"

    specialist_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=True)
    photo: Mapped[str] = mapped_column(String(200), nullable=True)
    years_of_experience: Mapped[int] = mapped_column(Integer, nullable=True)
    position: Mapped[str] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    devices: Mapped[List["Device"]] = relationship(
        "Device",
        secondary="specialist_device",
        back_populates="specialists"
    )