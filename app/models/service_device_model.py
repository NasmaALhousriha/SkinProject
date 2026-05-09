# app/models/specialist_device_model.py
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped
from app.database import Base

class ServiceDevice(Base):
    __tablename__ = "service_device"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.service_id"))
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.device_id"))
    assigned_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())