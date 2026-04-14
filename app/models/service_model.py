from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column


if TYPE_CHECKING:
    from .device_model import Device
    from .doctor_model import DoctorProfile

class Service(Base):
    __tablename__ = "services"

    service_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)

    devices: Mapped[list["Device"]] = relationship("Device", back_populates="service")
    doctors: Mapped[list["DoctorProfile"]] = relationship("DoctorProfile",secondary="doctor_services",back_populates="services")
