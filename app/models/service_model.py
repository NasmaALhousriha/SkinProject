from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from sqlalchemy.orm import Mapped, mapped_column


if TYPE_CHECKING:
    from .device_model import Device
    from .service_device_model import service_device
    from .doctor_model import DoctorProfile

class Service(Base):
    __tablename__ = "services"

    service_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(default=True)
    description: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    devices: Mapped[List["Device"]] = relationship(
        "Device",
        secondary="service_device",
        back_populates="services"
    )
    doctors: Mapped[list["DoctorProfile"]] =\
        relationship("DoctorProfile",
                     secondary="doctor_services",
                     back_populates="services")

