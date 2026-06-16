# app/models/device_model.py
from typing import List, TYPE_CHECKING, Optional
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from .specialist_model import Specialist
    from .service_model import Service
    from .service_device_model import service_device


class Device(Base):
    __tablename__ = "devices"

    device_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    services: Mapped[List["Service"]] = relationship(
        "Service",
        secondary="service_device",
        back_populates="devices"
    )


    specialists: Mapped[List["Specialist"]] = relationship(
        "Specialist",
        secondary="specialist_device",
        back_populates="devices"
    )