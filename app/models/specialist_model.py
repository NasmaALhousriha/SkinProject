from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import Integer, String, ForeignKey
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

    # relationships
    devices: Mapped[List["Device"]] = relationship("Device", back_populates="specialist")