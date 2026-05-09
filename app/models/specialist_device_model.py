# app/models/specialist_device_model.py
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped
from app.database import Base

class SpecialistDevice(Base):
    __tablename__ = "specialist_device"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    specialist_id: Mapped[int] = mapped_column(ForeignKey("specialists.specialist_id"))
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.device_id"))
    assigned_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())